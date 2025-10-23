"""Tests for security scanning module."""

import pytest
import tempfile
from pathlib import Path

from pipeline.security import SecurityScanner


def test_scan_safe_file():
    """Test scanning a safe file."""
    scanner = SecurityScanner()
    
    safe_code = """
def add(a, b):
    return a + b

def greet(name):
    return f"Hello, {name}!"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(safe_code)
        f.flush()
        
        is_safe, findings = scanner.scan_file(Path(f.name))
        
        assert is_safe
        assert len(findings) == 0
        
        Path(f.name).unlink()


def test_detect_secrets():
    """Test secret detection."""
    scanner = SecurityScanner(enable_secrets=True, enable_sast=False, enable_malware=False)
    
    code_with_secret = """
api_key = "sk_live_1234567890abcdefghijklmnop"
password = "super_secret_password123"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code_with_secret)
        f.flush()
        
        is_safe, findings = scanner.scan_file(Path(f.name))
        
        assert not is_safe
        assert len(findings) > 0
        assert any(f["type"] == "secret" for f in findings)
        
        Path(f.name).unlink()


def test_detect_dangerous_code():
    """Test SAST detection of dangerous code."""
    scanner = SecurityScanner(enable_sast=True, enable_secrets=False, enable_malware=False)
    
    dangerous_code = """
import os

def run_command(cmd):
    os.system(cmd)  # Dangerous!
    
def execute(code):
    eval(code)  # Also dangerous!
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(dangerous_code)
        f.flush()
        
        is_safe, findings = scanner.scan_file(Path(f.name))
        
        assert not is_safe
        assert len(findings) > 0
        assert any(f["type"] == "sast" for f in findings)
        
        Path(f.name).unlink()


def test_file_hash():
    """Test file hash computation."""
    scanner = SecurityScanner()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def foo(): pass")
        f.flush()
        
        hash1 = scanner.compute_file_hash(Path(f.name))
        assert len(hash1) == 64  # SHA-256
        
        # Same content should give same hash
        hash2 = scanner.compute_file_hash(Path(f.name))
        assert hash1 == hash2
        
        Path(f.name).unlink()
