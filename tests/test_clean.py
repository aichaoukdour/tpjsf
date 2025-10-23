"""Tests for cleaning module."""

import pytest
from pathlib import Path

from pipeline.clean import DataCleaner


def test_should_skip_file():
    """Test file skipping logic."""
    cleaner = DataCleaner(drop_tests=True)
    
    # Should skip test files
    skip, reason = cleaner.should_skip_file(Path("tests/test_foo.py"))
    assert skip
    assert "test" in reason.lower()
    
    # Should keep regular files
    skip, reason = cleaner.should_skip_file(Path("src/main.py"))
    assert not skip


def test_clean_content():
    """Test content cleaning."""
    cleaner = DataCleaner()
    
    content = """
def foo():
    return 42    
    
def bar():
    return "hello"  
"""
    
    cleaned = cleaner.clean_content(content)
    
    # Should remove trailing whitespace
    assert "    \n" not in cleaned
    assert "42    " not in cleaned


def test_compute_hash():
    """Test hash computation."""
    cleaner = DataCleaner()
    
    content1 = "def foo(): pass"
    content2 = "def bar(): pass"
    
    hash1 = cleaner.compute_hash(content1)
    hash2 = cleaner.compute_hash(content2)
    
    assert hash1 != hash2
    assert len(hash1) == 64  # SHA-256


def test_deduplication():
    """Test deduplication logic."""
    cleaner = DataCleaner()
    
    content = "def foo(): pass"
    hash1 = cleaner.compute_hash(content)
    
    # First time should not be duplicate
    assert not cleaner.is_duplicate(hash1)
    
    # Second time should be duplicate
    assert cleaner.is_duplicate(hash1)
    
    # Different content should not be duplicate
    hash2 = cleaner.compute_hash("def bar(): pass")
    assert not cleaner.is_duplicate(hash2)
