"""
Metrics computation and reporting.
Generates statistics about the curation process.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict


class MetricsCollector:
    """Collects and computes metrics for the pipeline."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = defaultdict(dict)
    
    def add_metric(self, category: str, key: str, value: Any):
        """Add a metric value."""
        self.metrics[category][key] = value
    
    def increment(self, category: str, key: str, amount: int = 1):
        """Increment a counter metric."""
        if key not in self.metrics[category]:
            self.metrics[category][key] = 0
        self.metrics[category][key] += amount
    
    def compute_discovery_metrics(self, discovery_report: Path) -> Dict[str, Any]:
        """Compute metrics from discovery phase."""
        if not discovery_report.exists():
            return {}
        
        import csv
        repos = []
        with open(discovery_report, 'r') as f:
            reader = csv.DictReader(f)
            repos = list(reader)
        
        metrics = {
            "total_repos_discovered": len(repos),
            "total_files_discovered": sum(int(r.get('file_count', 0)) for r in repos),
        }
        
        for key, value in metrics.items():
            self.add_metric("discovery", key, value)
        
        return metrics
    
    def compute_security_metrics(self, quarantine_dir: Path) -> Dict[str, Any]:
        """Compute security-related metrics."""
        quarantined_files = list(quarantine_dir.rglob("*.py")) if quarantine_dir.exists() else []
        
        metrics = {
            "total_quarantined": len(quarantined_files),
        }
        
        for key, value in metrics.items():
            self.add_metric("security", key, value)
        
        return metrics
    
    def compute_deduplication_metrics(self, 
                                      files_before: int,
                                      files_after: int) -> Dict[str, Any]:
        """Compute deduplication metrics."""
        duplicates_removed = files_before - files_after
        dedup_ratio = (duplicates_removed / files_before * 100) if files_before > 0 else 0
        
        metrics = {
            "files_before_dedup": files_before,
            "files_after_dedup": files_after,
            "duplicates_removed": duplicates_removed,
            "dedup_ratio_percent": round(dedup_ratio, 2),
        }
        
        for key, value in metrics.items():
            self.add_metric("cleaning", key, value)
        
        return metrics
    
    def compute_output_metrics(self, output_dir: Path) -> Dict[str, Any]:
        """Compute metrics for final outputs."""
        metrics = {}
        
        for split in ['train', 'val', 'test']:
            split_files = list(output_dir.rglob(f"{split}*.jsonl"))
            total_records = 0
            
            for file in split_files:
                with open(file, 'r') as f:
                    total_records += sum(1 for _ in f)
            
            metrics[f"{split}_records"] = total_records
        
        metrics["total_records"] = sum(v for k, v in metrics.items() if k.endswith('_records'))
        
        for key, value in metrics.items():
            self.add_metric("output", key, value)
        
        return metrics
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return dict(self.metrics)
    
    def save_metrics(self, output_path: str):
        """Save metrics to a JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.get_all_metrics(), f, indent=2)
        
        print(f"✅ Metrics saved to {output_path}")
    
    def print_summary(self):
        """Print a summary of metrics to console."""
        print("\n" + "="*60)
        print("📊 PIPELINE METRICS SUMMARY")
        print("="*60)
        
        for category, metrics in self.metrics.items():
            print(f"\n{category.upper()}:")
            for key, value in metrics.items():
                print(f"  • {key}: {value}")
        
        print("="*60 + "\n")
