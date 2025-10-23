"""Tests for license checking module."""

import pytest
import tempfile
from pathlib import Path

from pipeline.license import LicenseChecker


def test_detect_mit_license():
    """Test MIT license detection."""
    checker = LicenseChecker({"MIT"})
    
    license_text = """
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software...
"""
    
    detected = checker.detect_license(license_text)
    assert detected == "MIT"


def test_detect_apache_license():
    """Test Apache license detection."""
    checker = LicenseChecker({"Apache-2.0"})
    
    license_text = """
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/
"""
    
    detected = checker.detect_license(license_text)
    assert detected == "Apache-2.0"


def test_license_allowed():
    """Test license allowlist checking."""
    checker = LicenseChecker({"MIT", "Apache-2.0"})
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir)
        license_file = repo_dir / "LICENSE"
        
        license_file.write_text("""
MIT License

Permission is hereby granted, free of charge...
""")
        
        is_allowed, detected, reason = checker.check_repo(repo_dir)
        
        assert is_allowed
        assert detected == "MIT"


def test_license_not_allowed():
    """Test rejecting non-allowed licenses."""
    checker = LicenseChecker({"MIT"})
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir)
        license_file = repo_dir / "LICENSE"
        
        license_file.write_text("""
GNU General Public License
Version 3...
""")
        
        is_allowed, detected, reason = checker.check_repo(repo_dir)
        
        assert not is_allowed
        assert "GPL" in detected
