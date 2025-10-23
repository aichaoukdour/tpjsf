"""Metrics collection and reporting."""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class MetricsCollector:
    """Collects and reports pipeline metrics."""
    
    def __init__(self):
        self.metrics = {
            "run_info": {},
            "discovery": {},
            "compliance": {},
            "cleaning": {},
            "extraction": {},
            "output": {},
            "quality": {},
        }
    
    def set_run_info(self, run_id: str, config: Dict[str, Any]):
        """Set run information."""
        self.metrics["run_info"] = {
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "config": config,
        }
    
    def set_discovery_metrics(self, num_repos: int, successful: int):
        """Set discovery metrics."""
        self.metrics["discovery"] = {
            "repos_found": num_repos,
            "repos_cloned": successful,
            "success_rate": successful / num_repos if num_repos > 0 else 0,
        }
    
    def set_compliance_metrics(self, files_scanned: int, license_passed: int,
                              security_passed: int, quarantined: int):
        """Set compliance metrics."""
        self.metrics["compliance"] = {
            "files_scanned": files_scanned,
            "license_passed": license_passed,
            "security_passed": security_passed,
            "quarantined": quarantined,
            "pass_rate": (license_passed / files_scanned) if files_scanned > 0 else 0,
        }
    
    def set_cleaning_metrics(self, files_before: int, files_after: int, 
                           dedup_ratio: float):
        """Set cleaning metrics."""
        self.metrics["cleaning"] = {
            "files_before_cleaning": files_before,
            "files_after_cleaning": files_after,
            "files_removed": files_before - files_after,
            "dedup_ratio": dedup_ratio,
        }
    
    def set_extraction_metrics(self, task: str, examples_extracted: int,
                              avg_length: float, task_specific: Dict[str, Any]):
        """Set extraction metrics."""
        self.metrics["extraction"] = {
            "task": task,
            "examples_extracted": examples_extracted,
            "avg_example_length": avg_length,
            **task_specific,
        }
    
    def set_output_metrics(self, output_type: str, splits: Dict[str, int]):
        """Set output metrics."""
        self.metrics["output"] = {
            "format": output_type,
            "splits": splits,
            "total_records": sum(splits.values()),
        }
    
    def set_quality_metrics(self, quality_checks: Dict[str, Any]):
        """Set quality metrics."""
        self.metrics["quality"] = quality_checks
    
    def compute_quality_checks(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute quality checks on records."""
        if not records:
            return {}
        
        quality = {
            "total_records": len(records),
            "avg_input_length": sum(len(r["input"]) for r in records) / len(records),
            "avg_output_length": sum(len(r["output"]) for r in records) / len(records),
            "unique_repos": len(set(r["metadata"]["repo"] for r in records)),
        }
        
        # Task-specific quality checks
        if records[0]["task"] == "codegen":
            quality["with_docstring"] = sum(
                1 for r in records if r["metadata"].get("has_docstring", False)
            )
            quality["docstring_rate"] = quality["with_docstring"] / len(records)
        
        return quality
    
    def save_report(self, output_path: Path):
        """Save metrics report as JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dumps(self.metrics, f, indent=2)
            f.write(json.dumps(self.metrics, indent=2))
    
    def print_summary(self):
        """Print metrics summary to console."""
        print("\n" + "="*60)
        print("PIPELINE METRICS SUMMARY")
        print("="*60)
        
        if "run_info" in self.metrics and self.metrics["run_info"]:
            print(f"\nRun ID: {self.metrics['run_info'].get('run_id', 'N/A')}")
        
        if "discovery" in self.metrics and self.metrics["discovery"]:
            disc = self.metrics["discovery"]
            print(f"\nDiscovery:")
            print(f"  - Repositories cloned: {disc.get('repos_cloned', 0)}/{disc.get('repos_found', 0)}")
        
        if "compliance" in self.metrics and self.metrics["compliance"]:
            comp = self.metrics["compliance"]
            print(f"\nCompliance:")
            print(f"  - Files scanned: {comp.get('files_scanned', 0)}")
            print(f"  - License passed: {comp.get('license_passed', 0)}")
            print(f"  - Security passed: {comp.get('security_passed', 0)}")
            print(f"  - Quarantined: {comp.get('quarantined', 0)}")
        
        if "cleaning" in self.metrics and self.metrics["cleaning"]:
            clean = self.metrics["cleaning"]
            print(f"\nCleaning:")
            print(f"  - Files before: {clean.get('files_before_cleaning', 0)}")
            print(f"  - Files after: {clean.get('files_after_cleaning', 0)}")
            print(f"  - Dedup ratio: {clean.get('dedup_ratio', 0):.2%}")
        
        if "extraction" in self.metrics and self.metrics["extraction"]:
            extr = self.metrics["extraction"]
            print(f"\nExtraction ({extr.get('task', 'unknown')}):")
            print(f"  - Examples extracted: {extr.get('examples_extracted', 0)}")
            print(f"  - Avg length: {extr.get('avg_example_length', 0):.1f}")
        
        if "output" in self.metrics and self.metrics["output"]:
            out = self.metrics["output"]
            print(f"\nOutput ({out.get('format', 'unknown')}):")
            if "splits" in out:
                for split, count in out["splits"].items():
                    print(f"  - {split}: {count}")
        
        if "quality" in self.metrics and self.metrics["quality"]:
            qual = self.metrics["quality"]
            print(f"\nQuality:")
            for key, value in qual.items():
                if isinstance(value, float):
                    print(f"  - {key}: {value:.2f}")
                else:
                    print(f"  - {key}: {value}")
        
        print("\n" + "="*60 + "\n")
