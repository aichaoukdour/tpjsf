"""
Provenance logging module.
Tracks the lineage and processing history of each file.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ProvenanceLogger:
    """Logs provenance information for all processed files."""
    
    def __init__(self, log_path: str):
        """
        Initialize provenance logger.
        
        Args:
            log_path: Path to the JSONL log file
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create or append to log file
        if not self.log_path.exists():
            self.log_path.touch()
    
    def log_entry(self, 
                  file_path: str,
                  stage: str,
                  status: str,
                  metadata: Optional[Dict[str, Any]] = None):
        """
        Log a provenance entry.
        
        Args:
            file_path: Path to the file being processed
            stage: Pipeline stage (discover, license, security, clean, etc.)
            status: Status of the operation (success, failed, quarantined)
            metadata: Additional metadata to log
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "file_path": str(file_path),
            "file_hash": self._compute_hash(file_path) if Path(file_path).exists() else None,
            "stage": stage,
            "status": status,
            "metadata": metadata or {}
        }
        
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _compute_hash(self, file_path: str) -> str:
        """Compute SHA256 hash of a file."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None
    
    def get_entries(self, file_path: Optional[str] = None) -> list:
        """
        Retrieve log entries, optionally filtered by file path.
        
        Args:
            file_path: Optional file path to filter entries
            
        Returns:
            List of log entries
        """
        entries = []
        
        if not self.log_path.exists():
            return entries
        
        with open(self.log_path, 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                if file_path is None or entry['file_path'] == str(file_path):
                    entries.append(entry)
        
        return entries
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from the provenance log."""
        entries = self.get_entries()
        
        stats = {
            "total_entries": len(entries),
            "by_stage": {},
            "by_status": {},
            "unique_files": len(set(e['file_path'] for e in entries))
        }
        
        for entry in entries:
            stage = entry['stage']
            status = entry['status']
            
            stats['by_stage'][stage] = stats['by_stage'].get(stage, 0) + 1
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        return stats
