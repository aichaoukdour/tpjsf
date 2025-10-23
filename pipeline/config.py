"""Configuration management for the pipeline."""

from dataclasses import dataclass, field
from typing import List, Optional
import yaml
from pathlib import Path


@dataclass
class GitHubSourceConfig:
    """GitHub source configuration."""
    query: str = "language:Python stars:>100"
    max_repos: int = 20
    token: Optional[str] = None  # GitHub API token (optional)


@dataclass
class SourcesConfig:
    """Data sources configuration."""
    github: GitHubSourceConfig = field(default_factory=GitHubSourceConfig)
    local_datasets: List[str] = field(default_factory=list)


@dataclass
class ComplianceConfig:
    """License compliance configuration."""
    license_allow: List[str] = field(
        default_factory=lambda: ["MIT", "BSD", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause"]
    )


@dataclass
class SecurityConfig:
    """Security scanning configuration."""
    enable_sast: bool = True
    enable_secrets: bool = True
    enable_malware: bool = True


@dataclass
class CleaningConfig:
    """Data cleaning configuration."""
    drop_tests: bool = True
    max_file_mb: float = 1.0
    dedupe_level: str = "function"  # file | function
    min_line_length: int = 3
    max_line_length: int = 1000


@dataclass
class OutputConfig:
    """Output configuration."""
    type: str = "finetune"  # finetune | rag
    version: str = "v1"
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1


@dataclass
class PipelineConfig:
    """Main pipeline configuration."""
    run_id: str = "trial-001"
    sources: SourcesConfig = field(default_factory=SourcesConfig)
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    cleaning: CleaningConfig = field(default_factory=CleaningConfig)
    branch: str = "codegen"  # debugging | codegen | refactor | docs
    output: OutputConfig = field(default_factory=OutputConfig)
    
    # Paths
    data_dir: Path = field(default_factory=lambda: Path("data"))
    reports_dir: Path = field(default_factory=lambda: Path("reports"))
    schemas_dir: Path = field(default_factory=lambda: Path("schemas"))
    
    @classmethod
    def from_yaml(cls, path: str) -> "PipelineConfig":
        """Load configuration from YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        
        # Build nested configs
        config = cls()
        config.run_id = data.get("run_id", config.run_id)
        config.branch = data.get("branch", config.branch)
        
        # Sources
        if "sources" in data:
            sources = data["sources"]
            if "github" in sources:
                gh = sources["github"]
                config.sources.github = GitHubSourceConfig(
                    query=gh.get("query", config.sources.github.query),
                    max_repos=gh.get("max_repos", config.sources.github.max_repos),
                    token=gh.get("token")
                )
            config.sources.local_datasets = sources.get("local_datasets", [])
        
        # Compliance
        if "compliance" in data:
            config.compliance.license_allow = data["compliance"].get(
                "license_allow", config.compliance.license_allow
            )
        
        # Security
        if "security" in data:
            sec = data["security"]
            config.security.enable_sast = sec.get("enable_sast", config.security.enable_sast)
            config.security.enable_secrets = sec.get("enable_secrets", config.security.enable_secrets)
            config.security.enable_malware = sec.get("enable_malware", config.security.enable_malware)
        
        # Cleaning
        if "cleaning" in data:
            clean = data["cleaning"]
            config.cleaning.drop_tests = clean.get("drop_tests", config.cleaning.drop_tests)
            config.cleaning.max_file_mb = clean.get("max_file_mb", config.cleaning.max_file_mb)
            config.cleaning.dedupe_level = clean.get("dedupe_level", config.cleaning.dedupe_level)
        
        # Output
        if "output" in data:
            out = data["output"]
            config.output.type = out.get("type", config.output.type)
            config.output.version = out.get("version", config.output.version)
        
        return config
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "run_id": self.run_id,
            "sources": {
                "github": {
                    "query": self.sources.github.query,
                    "max_repos": self.sources.github.max_repos,
                },
                "local_datasets": self.sources.local_datasets,
            },
            "compliance": {
                "license_allow": self.compliance.license_allow,
            },
            "security": {
                "enable_sast": self.security.enable_sast,
                "enable_secrets": self.security.enable_secrets,
                "enable_malware": self.security.enable_malware,
            },
            "cleaning": {
                "drop_tests": self.cleaning.drop_tests,
                "max_file_mb": self.cleaning.max_file_mb,
                "dedupe_level": self.cleaning.dedupe_level,
            },
            "branch": self.branch,
            "output": {
                "type": self.output.type,
                "version": self.output.version,
            },
        }
