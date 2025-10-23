"""Security scanning for secrets, SAST, and malware."""

import re
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Any
import hashlib


class SecurityScanner:
    """Performs security checks on code files."""
    
    # Common secret patterns
    SECRET_PATTERNS = [
        (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "API Key"),
        (r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "Secret Key"),
        (r'(?i)(password)\s*[:=]\s*["\']([^"\']{8,})["\']', "Hardcoded Password"),
        (r'(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[:=]\s*["\']([A-Z0-9]{20})["\']', "AWS Access Key"),
        (r'(?i)(private[_-]?key)\s*[:=]\s*["\']([^\'"]+)["\']', "Private Key"),
        (r'ghp_[a-zA-Z0-9]{36}', "GitHub Token"),
        (r'gho_[a-zA-Z0-9]{36}', "GitHub OAuth Token"),
        (r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}', "GitHub PAT"),
    ]
    
    # Suspicious code patterns (simple SAST)
    SAST_PATTERNS = [
        (r'eval\s*\(', "Use of eval()"),
        (r'exec\s*\(', "Use of exec()"),
        (r'__import__\s*\(', "Dynamic import"),
        (r'pickle\.loads?\s*\(', "Pickle deserialization"),
        (r'subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True', "Shell injection risk"),
        (r'os\.system\s*\(', "OS command execution"),
    ]
    
    # Malware indicators
    MALWARE_PATTERNS = [
        (r'(?i)reverse[_-]?shell', "Reverse shell indicator"),
        (r'(?i)cryptominer|crypto[_-]?miner', "Cryptominer indicator"),
        (r'(?i)keylogger', "Keylogger indicator"),
        (r'(?i)ransomware', "Ransomware indicator"),
        (r'base64\.b64decode\s*\(\s*["\'][A-Za-z0-9+/=]{100,}["\']', "Large base64 payload"),
    ]
    
    def __init__(self, enable_sast: bool = True, enable_secrets: bool = True, enable_malware: bool = True):
        self.enable_sast = enable_sast
        self.enable_secrets = enable_secrets
        self.enable_malware = enable_malware
    
    def scan_file(self, file_path: Path) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Scan a file for security issues.
        
        Returns:
            (is_safe, findings)
        """
        findings = []
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            return False, [{"type": "error", "message": f"Cannot read file: {e}"}]
        
        # Check for secrets
        if self.enable_secrets:
            secret_findings = self._check_secrets(content)
            findings.extend(secret_findings)
        
        # SAST checks
        if self.enable_sast:
            sast_findings = self._check_sast(content)
            findings.extend(sast_findings)
        
        # Malware checks
        if self.enable_malware:
            malware_findings = self._check_malware(content)
            findings.extend(malware_findings)
        
        # File is safe if no findings
        is_safe = len(findings) == 0
        return is_safe, findings
    
    def _check_secrets(self, content: str) -> List[Dict[str, Any]]:
        """Check for hardcoded secrets."""
        findings = []
        for pattern, description in self.SECRET_PATTERNS:
            matches = re.finditer(pattern, content)
            for match in matches:
                findings.append({
                    "type": "secret",
                    "description": description,
                    "pattern": pattern,
                    "location": match.span()
                })
        return findings
    
    def _check_sast(self, content: str) -> List[Dict[str, Any]]:
        """Static application security testing."""
        findings = []
        for pattern, description in self.SAST_PATTERNS:
            matches = re.finditer(pattern, content)
            for match in matches:
                findings.append({
                    "type": "sast",
                    "description": description,
                    "pattern": pattern,
                    "location": match.span()
                })
        return findings
    
    def _check_malware(self, content: str) -> List[Dict[str, Any]]:
        """Check for malware indicators."""
        findings = []
        for pattern, description in self.MALWARE_PATTERNS:
            matches = re.finditer(pattern, content)
            for match in matches:
                findings.append({
                    "type": "malware",
                    "description": description,
                    "pattern": pattern,
                    "location": match.span()
                })
        return findings
    
    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return ""
