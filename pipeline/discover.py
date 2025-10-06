"""
Discovery module for finding and collecting Python repositories.
Supports local directories, GitHub API, and URL downloads.
"""

import csv
import shutil
from pathlib import Path
from typing import List, Dict, Any
import subprocess


class RepositoryDiscoverer:
    """Discovers and downloads Python repositories."""
    
    def __init__(self, config, logger):
        """
        Initialize discoverer.
        
        Args:
            config: PipelineConfig instance
            logger: ProvenanceLogger instance
        """
        self.config = config
        self.logger = logger
        self.raw_dir = Path(config.data_dir) / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
    
    def discover(self) -> List[Dict[str, Any]]:
        """
        Discover repositories based on configuration.
        
        Returns:
            List of repository metadata dictionaries
        """
        print(f"🔍 Discovering repositories (mode: {self.config.discovery_mode})...")
        
        if self.config.discovery_mode == "local":
            repos = self._discover_local()
        elif self.config.discovery_mode == "github":
            repos = self._discover_github()
        elif self.config.discovery_mode == "url":
            repos = self._discover_url()
        else:
            raise ValueError(f"Unknown discovery mode: {self.config.discovery_mode}")
        
        # Limit to max_repos
        repos = repos[:self.config.max_repos]
        
        print(f"✅ Discovered {len(repos)} repositories")
        return repos
    
    def _discover_local(self) -> List[Dict[str, Any]]:
        """Discover local repositories or directories."""
        repos = []
        
        for source in self.config.discovery_sources:
            source_path = Path(source)
            
            if not source_path.exists():
                print(f"⚠️  Source not found: {source}")
                self.logger.log_entry(
                    file_path=str(source_path),
                    stage="discover",
                    status="failed",
                    metadata={"reason": "path_not_found"}
                )
                continue
            
            # Copy to raw directory
            dest_name = source_path.name
            dest_path = self.raw_dir / dest_name
            
            if source_path.is_dir():
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path, 
                              ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '.git'))
            else:
                shutil.copy2(source_path, dest_path)
            
            # Count Python files
            py_files = list(dest_path.rglob("*.py")) if dest_path.is_dir() else [dest_path]
            
            repo_info = {
                "name": dest_name,
                "source": str(source_path),
                "destination": str(dest_path),
                "type": "local",
                "file_count": len(py_files),
            }
            
            repos.append(repo_info)
            
            self.logger.log_entry(
                file_path=str(dest_path),
                stage="discover",
                status="success",
                metadata=repo_info
            )
        
        return repos
    
    def _discover_github(self) -> List[Dict[str, Any]]:
        """Discover repositories from GitHub."""
        # Placeholder implementation - would use PyGithub in production
        repos = []
        
        print("⚠️  GitHub discovery is a placeholder implementation")
        
        for source in self.config.discovery_sources:
            # source format: "owner/repo" or GitHub URL
            repo_name = source.split('/')[-1] if '/' in source else source
            dest_path = self.raw_dir / repo_name
            
            # Simulate repository download
            repo_info = {
                "name": repo_name,
                "source": source,
                "destination": str(dest_path),
                "type": "github",
                "file_count": 0,
            }
            
            repos.append(repo_info)
            
            self.logger.log_entry(
                file_path=str(dest_path),
                stage="discover",
                status="success",
                metadata=repo_info
            )
        
        return repos
    
    def _discover_url(self) -> List[Dict[str, Any]]:
        """Discover repositories from URLs."""
        # Placeholder implementation
        repos = []
        
        print("⚠️  URL discovery is a placeholder implementation")
        
        for source in self.config.discovery_sources:
            repo_name = Path(source).stem
            dest_path = self.raw_dir / repo_name
            
            repo_info = {
                "name": repo_name,
                "source": source,
                "destination": str(dest_path),
                "type": "url",
                "file_count": 0,
            }
            
            repos.append(repo_info)
            
            self.logger.log_entry(
                file_path=str(dest_path),
                stage="discover",
                status="success",
                metadata=repo_info
            )
        
        return repos
    
    def save_report(self, repos: List[Dict[str, Any]], report_path: str):
        """Save discovery report to CSV."""
        report_file = Path(report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', newline='') as f:
            if repos:
                writer = csv.DictWriter(f, fieldnames=repos[0].keys())
                writer.writeheader()
                writer.writerows(repos)
        
        print(f"📝 Discovery report saved to {report_path}")
