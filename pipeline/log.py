"""Provenance and audit logging."""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class ProvenanceLogger:
    """Logs provenance information for all processed files."""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.entries = []
    
    def log(self, entry: Dict[str, Any]):
        """Log a single provenance entry."""
        entry["timestamp"] = datetime.utcnow().isoformat()
        self.entries.append(entry)
    
    def flush(self):
        """Write all entries to disk."""
        with open(self.log_path, "w") as f:
            for entry in self.entries:
                f.write(json.dumps(entry) + "\n")


class QuarantineLogger:
    """Logs quarantined items (license/security failures)."""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.entries = []
    
    def log(self, repo: str, path: str, reason: str, checker: str, evidence: str = ""):
        """Log a quarantined file."""
        self.entries.append({
            "repo": repo,
            "path": path,
            "reason": reason,
            "checker": checker,
            "evidence": evidence,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def flush(self):
        """Write all entries to CSV."""
        if not self.entries:
            return
        
        with open(self.log_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["repo", "path", "reason", "checker", "evidence", "timestamp"])
            writer.writeheader()
            writer.writerows(self.entries)


class DiscoveryLogger:
    """Logs discovered repositories."""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.entries = []
    
    def log(self, repo: str, commit_sha: str, size: int, stars: int, fetched_at: str):
        """Log a discovered repository."""
        self.entries.append({
            "repo": repo,
            "commit_sha": commit_sha,
            "size": size,
            "stars": stars,
            "fetched_at": fetched_at
        })
    
    def flush(self):
        """Write all entries to CSV."""
        if not self.entries:
            return
        
        with open(self.log_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["repo", "commit_sha", "size", "stars", "fetched_at"])
            writer.writeheader()
            writer.writerows(self.entries)
