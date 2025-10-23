"""Tests for transformation module."""

import pytest

from pipeline.transform import SchemaTransformer


def test_transform_codegen():
    """Test code generation transformation."""
    transformer = SchemaTransformer("codegen")
    
    example = {
        "signature": "def add(a: int, b: int) -> int:",
        "docstring": "Add two numbers.",
        "body": "    return a + b",
        "metadata": {
            "repo": "owner/repo",
            "path": "src/math.py",
            "commit": "abc123",
            "license": "MIT",
            "function_name": "add",
            "num_lines": 3,
            "has_docstring": True,
        }
    }
    
    record = transformer.transform_codegen(example, split="train")
    
    assert record["task"] == "codegen"
    assert "def add" in record["input"]
    assert "return a + b" in record["output"]
    assert record["metadata"]["split"] == "train"
    assert record["metadata"]["repo"] == "owner/repo"


def test_validate_record():
    """Test record validation."""
    transformer = SchemaTransformer("codegen")
    
    valid_record = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "task": "codegen",
        "input": "def foo():",
        "output": "pass",
        "metadata": {
            "repo": "owner/repo",
            "path": "file.py",
            "commit": "abc",
            "license": "MIT",
            "hash": "sha256:abc",
            "checks": {
                "license": "pass",
                "secrets": "pass",
                "sast": "pass",
            },
            "split": "train",
        }
    }
    
    assert transformer.validate_record(valid_record)
    
    # Invalid record (missing required field)
    invalid_record = {
        "id": "123",
        "task": "codegen",
        "input": "test",
    }
    
    assert not transformer.validate_record(invalid_record)
