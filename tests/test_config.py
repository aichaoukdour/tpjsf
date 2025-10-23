"""Tests for configuration module."""

import pytest
import tempfile
from pathlib import Path
import yaml

from pipeline.config import PipelineConfig


def test_default_config():
    """Test default configuration."""
    config = PipelineConfig()
    
    assert config.run_id == "trial-001"
    assert config.branch == "codegen"
    assert config.sources.github.max_repos == 20
    assert "MIT" in config.compliance.license_allow


def test_config_from_yaml():
    """Test loading config from YAML."""
    yaml_content = """
run_id: "test-run"
branch: "codegen"
sources:
  github:
    query: "language:Python"
    max_repos: 5
compliance:
  license_allow:
    - "MIT"
output:
  type: "finetune"
  version: "v1"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        f.flush()
        
        config = PipelineConfig.from_yaml(f.name)
        
        assert config.run_id == "test-run"
        assert config.sources.github.max_repos == 5
        assert config.compliance.license_allow == ["MIT"]
        
        Path(f.name).unlink()


def test_config_to_dict():
    """Test converting config to dictionary."""
    config = PipelineConfig()
    config_dict = config.to_dict()
    
    assert "run_id" in config_dict
    assert "sources" in config_dict
    assert "branch" in config_dict
