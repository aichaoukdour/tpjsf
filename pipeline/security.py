"""
Security scanning module.
Checks for secrets, vulnerabilities, and malware patterns.
"""

import re
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple


class SecurityScanner:
    """Scans code for security issues."""
    
    def __init__(self, config, logger):
        """
        Initialize security scanner.
        
        Args:
            config: PipelineConfig instance
            logger: ProvenanceLogger instance
        """
        self.config = config
        self.logger = logger
        self.quarantine_dir = Path(config.data_dir) / "quarantine" / "security"
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        
        # Security patterns (simplified for demo)
        self.secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "hardcoded_password"),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "api_key"),
            (r'secret[_-]?key\s*=\s*["\'][^"\']+["\']', "secret_key"),
            (r'aws[_-]?access[_-]?key', "aws_credentials"),
            (r'["\'][0-9a-f]{32,}["\']', "potential_token"),
        ]
        
        self.vulnerability_patterns = [
            (r'eval\s*\(', "eval_usage"),
            (r'exec\s*\(', "exec_usage"),
            (r'__import__\s*\(', "dynamic_import"),
            (r'pickle\.loads?\s*\(', "unsafe_pickle"),
            (r'subprocess\.(call|run|Popen).*shell\s*=\s*True', "shell_injection_risk"),
        ]
    
    def scan_file(self, file_path: Path) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Scan a single file for security issues.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (is_safe, list of findings)
        """
        findings = []
        
        try:
            content = file_path.read_text(errors='ignore')
            
            # Check for secrets
            if "secrets" in self.config.security_checks:
                for pattern, issue_type in self.secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        findings.append({
                            "type": "secret",
                            "issue": issue_type,
                            "line": content[:match.start()].count('\n') + 1,
                            "severity": "high",
                        })
            
            # Check for vulnerabilities (Bandit-style)
            if "bandit" in self.config.security_checks:
                for pattern, issue_type in self.vulnerability_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        findings.append({
                            "type": "vulnerability",
                            "issue": issue_type,
                            "line": content[:match.start()].count('\n') + 1,
                            "severity": "medium",
                        })
            
            # Simple malware check
            if "malware" in self.config.security_checks:
                malware_keywords = ['ransom', 'keylogger', 'backdoor']
                content_lower = content.lower()
                for keyword in malware_keywords:
                    if keyword in content_lower:
                        findings.append({
                            "type": "malware",
                            "issue": f"suspicious_keyword_{keyword}",
                            "severity": "critical",
                        })
        
        except Exception as e:
            findings.append({
                "type": "error",
                "issue": "scan_failed",
                "error": str(e),
                "severity": "unknown",
            })
        
        # Filter by severity threshold
        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        threshold = severity_order.get(self.config.bandit_severity, 1)
        
        critical_findings = [
            f for f in findings 
            if severity_order.get(f.get("severity", "low"), 0) >= threshold
        ]
        
        is_safe = len(critical_findings) == 0
        
        return is_safe, findings
    
    def scan_all(self, raw_dir: Path) -> Dict[str, Any]:
        """
        Scan all Python files for security issues.
        
        Args:
            raw_dir: Path to raw data directory
            
        Returns:
            Dictionary with scan results
        """
        print(f"🔒 Scanning for security issues...")
        
        results = {
            "safe_files": [],
            "unsafe_files": [],
            "quarantined_files": [],
            "total_findings": 0,
        }
        
        # Find all Python files
        py_files = list(raw_dir.rglob("*.py"))
        
        for py_file in py_files:
            is_safe, findings = self.scan_file(py_file)
            
            if is_safe:
                results["safe_files"].append(str(py_file))
                self.logger.log_entry(
                    file_path=str(py_file),
                    stage="security",
                    status="success",
                    metadata={"findings_count": len(findings)}
                )
            else:
                # Quarantine unsafe file
                rel_path = py_file.relative_to(raw_dir)
                quarantine_path = self.quarantine_dir / rel_path
                quarantine_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.move(str(py_file), str(quarantine_path))
                
                results["unsafe_files"].append(str(py_file))
                results["quarantined_files"].append(str(quarantine_path))
                results["total_findings"] += len(findings)
                
                self.logger.log_entry(
                    file_path=str(quarantine_path),
                    stage="security",
                    status="quarantined",
                    metadata={
                        "findings_count": len(findings),
                        "findings": findings[:5],  # Store first 5 findings
                    }
                )
        
        print(f"✅ Security scan complete: {len(results['safe_files'])} safe files, "
              f"{len(results['unsafe_files'])} quarantined")
        
        return results
