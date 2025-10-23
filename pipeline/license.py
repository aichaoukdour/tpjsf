"""License compliance checking."""

import re
from pathlib import Path
from typing import Optional, Set, Tuple
import subprocess


class LicenseChecker:
    """Checks repository licenses for compliance."""
    
    # Common license file names
    LICENSE_FILES = [
        "LICENSE", "LICENSE.txt", "LICENSE.md", "LICENSE.rst",
        "COPYING", "COPYING.txt", "COPYING.md",
        "license", "license.txt", "license.md"
    ]
    
    # Simple license detection patterns
    LICENSE_PATTERNS = {
        "MIT": [
            r"MIT License",
            r"Permission is hereby granted, free of charge",
        ],
        "Apache-2.0": [
            r"Apache License",
            r"Version 2\.0",
        ],
        "BSD": [
            r"BSD License",
            r"Redistributions of source code must retain",
        ],
        "BSD-3-Clause": [
            r"BSD 3-Clause",
            r"Redistributions of source code must retain",
        ],
        "BSD-2-Clause": [
            r"BSD 2-Clause",
            r"Redistributions of source code must retain",
        ],
        "GPL": [
            r"GNU General Public License",
            r"GPL",
        ],
        "LGPL": [
            r"GNU Lesser General Public License",
            r"LGPL",
        ],
    }
    
    def __init__(self, allowed_licenses: Set[str]):
        self.allowed_licenses = {lic.upper() for lic in allowed_licenses}
        # Also allow variations
        self.allowed_variations = set()
        for lic in allowed_licenses:
            self.allowed_variations.add(lic.upper())
            if "BSD" in lic.upper():
                self.allowed_variations.add("BSD")
    
    def find_license_file(self, repo_dir: Path) -> Optional[Path]:
        """Find the license file in a repository."""
        for filename in self.LICENSE_FILES:
            license_path = repo_dir / filename
            if license_path.exists():
                return license_path
        return None
    
    def detect_license(self, license_text: str) -> Optional[str]:
        """Detect license type from license text."""
        license_text_upper = license_text.upper()
        
        for license_name, patterns in self.LICENSE_PATTERNS.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, license_text, re.IGNORECASE))
            if matches >= 1:  # At least one pattern matches
                return license_name
        
        return None
    
    def check_repo(self, repo_dir: Path) -> Tuple[bool, Optional[str], str]:
        """
        Check if repository license is compliant.
        
        Returns:
            (is_allowed, detected_license, reason)
        """
        license_file = self.find_license_file(repo_dir)
        
        if not license_file:
            return False, None, "No license file found"
        
        try:
            with open(license_file, "r", encoding="utf-8", errors="ignore") as f:
                license_text = f.read()
        except Exception as e:
            return False, None, f"Error reading license file: {e}"
        
        detected_license = self.detect_license(license_text)
        
        if not detected_license:
            return False, None, "Could not detect license type"
        
        # Check if detected license is allowed
        if detected_license.upper() in self.allowed_variations:
            return True, detected_license, "License allowed"
        
        # Special case: GPL/LGPL are typically not allowed for commercial use
        if "GPL" in detected_license.upper():
            return False, detected_license, f"License {detected_license} not in allowed list"
        
        return False, detected_license, f"License {detected_license} not in allowed list"
    
    def check_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Check if a file has license headers (optional check).
        
        Returns:
            (has_license_header, detected_license)
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                # Read first 50 lines
                lines = [f.readline() for _ in range(50)]
                header_text = "".join(lines)
            
            detected = self.detect_license(header_text)
            return detected is not None, detected or "None"
        
        except Exception:
            return False, "Error"
