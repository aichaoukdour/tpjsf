"""Repository discovery and ingestion from GitHub."""

import os
import subprocess
import requests
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import time

from .config import PipelineConfig
from .log import DiscoveryLogger


class RepositoryDiscovery:
    """Discovers and clones Python repositories from GitHub."""
    
    def __init__(self, config: PipelineConfig, logger: DiscoveryLogger):
        self.config = config
        self.logger = logger
        self.github_token = config.sources.github.token or os.getenv("GITHUB_TOKEN")
    
    def search_github_repos(self) -> List[Dict[str, Any]]:
        """Search GitHub for Python repositories."""
        query = self.config.sources.github.query
        max_repos = self.config.sources.github.max_repos
        
        headers = {}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        repos = []
        page = 1
        per_page = min(100, max_repos)
        
        while len(repos) < max_repos:
            url = f"https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": per_page,
                "page": page
            }
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("items"):
                    break
                
                repos.extend(data["items"])
                
                if len(repos) >= max_repos or len(data["items"]) < per_page:
                    break
                
                page += 1
                time.sleep(1)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error searching GitHub: {e}")
                break
        
        return repos[:max_repos]
    
    def clone_repo(self, repo_info: Dict[str, Any], output_dir: Path) -> bool:
        """Clone a repository to the output directory."""
        repo_name = repo_info["full_name"]
        clone_url = repo_info["clone_url"]
        repo_dir = output_dir / repo_name.replace("/", "_")
        
        if repo_dir.exists():
            print(f"Repository {repo_name} already exists, skipping...")
            return True
        
        try:
            repo_dir.parent.mkdir(parents=True, exist_ok=True)
            
            # Clone with depth 1 for faster cloning
            subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, str(repo_dir)],
                check=True,
                capture_output=True,
                timeout=300
            )
            
            # Get commit SHA
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_dir,
                check=True,
                capture_output=True,
                text=True
            )
            commit_sha = result.stdout.strip()
            
            # Log discovery
            self.logger.log(
                repo=repo_name,
                commit_sha=commit_sha,
                size=repo_info.get("size", 0),
                stars=repo_info.get("stargazers_count", 0),
                fetched_at=datetime.utcnow().isoformat()
            )
            
            return True
            
        except subprocess.TimeoutExpired:
            print(f"Timeout cloning {repo_name}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Error cloning {repo_name}: {e}")
            return False
    
    def discover_and_fetch(self) -> int:
        """Main discovery and fetch process."""
        print("Searching GitHub for repositories...")
        repos = self.search_github_repos()
        print(f"Found {len(repos)} repositories")
        
        output_dir = self.config.data_dir / "raw"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        successful = 0
        for i, repo_info in enumerate(repos, 1):
            repo_name = repo_info["full_name"]
            print(f"[{i}/{len(repos)}] Cloning {repo_name}...")
            
            if self.clone_repo(repo_info, output_dir):
                successful += 1
        
        self.logger.flush()
        print(f"Successfully cloned {successful}/{len(repos)} repositories")
        return successful
