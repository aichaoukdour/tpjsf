"""
Configuration management for the pipeline.
Loads and validates configuration from YAML files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    """Main configuration for the curation pipeline."""
    
    # Discovery settings
    discovery_mode: str = "local"  # local, github, or url
    discovery_sources: List[str] = field(default_factory=list)
    max_repos: int = 10
    
    # License settings
    allowed_licenses: List[str] = field(default_factory=lambda: [
        "MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "Python-2.0"
    ])
    license_strict: bool = True
    
    # Security settings
    security_checks: List[str] = field(default_factory=lambda: ["bandit", "secrets", "malware"])
    bandit_severity: str = "medium"  # low, medium, high
    
    # Cleaning settings
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "*/test/*", "*/tests/*", "*/vendor/*", "*/node_modules/*",
        "*/__pycache__/*", "*.pyc", "*.pyo", "*.egg-info/*"
    ])
    min_file_size: int = 10  # bytes
    max_file_size: int = 1048576  # 1MB
    format_code: bool = True
    
    # Task branch
    task_branch: str = "codegen"  # codegen, debugging, refactor, docs
    
    # Output settings
    output_formats: List[str] = field(default_factory=lambda: ["ft", "rag"])
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    
    # Paths
    data_dir: str = "data"
    reports_dir: str = "reports"
    schema_path: str = "schemas/common.schema.json"
    
    # Misc
    random_seed: int = 42
    deterministic: bool = True
    
    @classmethod
    def from_yaml(cls, path: str) -> 'PipelineConfig':
        """Load configuration from a YAML file."""
        config_path = Path(path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "discovery_mode": self.discovery_mode,
            "discovery_sources": self.discovery_sources,
            "max_repos": self.max_repos,
            "allowed_licenses": self.allowed_licenses,
            "license_strict": self.license_strict,
            "security_checks": self.security_checks,
            "bandit_severity": self.bandit_severity,
            "exclude_patterns": self.exclude_patterns,
            "min_file_size": self.min_file_size,
            "max_file_size": self.max_file_size,
            "format_code": self.format_code,
            "task_branch": self.task_branch,
            "output_formats": self.output_formats,
            "train_split": self.train_split,
            "val_split": self.val_split,
            "test_split": self.test_split,
            "data_dir": self.data_dir,
            "reports_dir": self.reports_dir,
            "schema_path": self.schema_path,
            "random_seed": self.random_seed,
            "deterministic": self.deterministic,
        }
    
    def validate(self):
        """Validate configuration values."""
        # Check splits add up to 1.0
        total_split = self.train_split + self.val_split + self.test_split
        if abs(total_split - 1.0) > 0.001:
            raise ValueError(f"Train/val/test splits must sum to 1.0, got {total_split}")
        
        # Check valid task branch
        valid_branches = ["codegen", "debugging", "refactor", "docs"]
        if self.task_branch not in valid_branches:
            raise ValueError(f"Invalid task_branch: {self.task_branch}. Must be one of {valid_branches}")
        
        # Check valid discovery mode
        valid_modes = ["local", "github", "url"]
        if self.discovery_mode not in valid_modes:
            raise ValueError(f"Invalid discovery_mode: {self.discovery_mode}. Must be one of {valid_modes}")
        
        return True
