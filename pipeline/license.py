"""
License scanning and validation module.
Checks repository licenses against allowed list.
"""

import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple


class LicenseScanner:
    """Scans and validates licenses for repositories."""
    
    def __init__(self, config, logger):
        """
        Initialize license scanner.
        
        Args:
            config: PipelineConfig instance
            logger: ProvenanceLogger instance
        """
        self.config = config
        self.logger = logger
        self.quarantine_dir = Path(config.data_dir) / "quarantine" / "license"
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
    
    def scan_repository(self, repo_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """
        Scan a repository for license compliance.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Tuple of (is_compliant, metadata)
        """
        # Realistic dummy implementation
        # In production, would use scancode-toolkit or license-expression
        
        detected_licenses = self._detect_licenses(repo_path)
        
        is_compliant = False
        if detected_licenses:
            is_compliant = any(
                lic in self.config.allowed_licenses 
                for lic in detected_licenses
            )
        elif not self.config.license_strict:
            # If not strict mode, allow repos without explicit license
            is_compliant = True
        
        metadata = {
            "detected_licenses": detected_licenses,
            "allowed_licenses": self.config.allowed_licenses,
            "is_compliant": is_compliant,
            "strict_mode": self.config.license_strict,
        }
        
        return is_compliant, metadata
    
    def _detect_licenses(self, repo_path: Path) -> List[str]:
        """
        Detect licenses in a repository.
        
        This is a simplified implementation that looks for common license files.
        In production, use scancode-toolkit for accurate detection.
        """
        license_files = [
            "LICENSE", "LICENSE.txt", "LICENSE.md",
            "COPYING", "COPYING.txt",
            "LICENSE-MIT", "LICENSE-APACHE",
        ]
        
        detected = []
        
        for license_file in license_files:
            license_path = repo_path / license_file
            if license_path.exists():
                # Simple keyword matching
                content = license_path.read_text(errors='ignore').upper()
                
                if "MIT LICENSE" in content or "MIT" in content[:200]:
                    detected.append("MIT")
                elif "APACHE" in content[:300]:
                    if "2.0" in content[:300]:
                        detected.append("Apache-2.0")
                    else:
                        detected.append("Apache")
                elif "BSD" in content[:300]:
                    if "3-CLAUSE" in content or "THREE CLAUSE" in content:
                        detected.append("BSD-3-Clause")
                    elif "2-CLAUSE" in content or "TWO CLAUSE" in content:
                        detected.append("BSD-2-Clause")
                    else:
                        detected.append("BSD")
                elif "ISC LICENSE" in content:
                    detected.append("ISC")
                elif "PYTHON" in content:
                    detected.append("Python-2.0")
        
        # Default to MIT if no license found (for demo purposes)
        if not detected and not self.config.license_strict:
            detected.append("MIT")
        
        return list(set(detected))
    
    def scan_all(self, raw_dir: Path) -> Dict[str, Any]:
        """
        Scan all repositories in the raw directory.
        
        Args:
            raw_dir: Path to raw data directory
            
        Returns:
            Dictionary with scan results
        """
        print(f"📜 Scanning licenses...")
        
        results = {
            "compliant": [],
            "non_compliant": [],
            "quarantined": [],
        }
        
        # Find all repositories/directories
        repos = [p for p in raw_dir.iterdir() if p.is_dir()]
        
        for repo_path in repos:
            is_compliant, metadata = self.scan_repository(repo_path)
            
            if is_compliant:
                results["compliant"].append(str(repo_path))
                self.logger.log_entry(
                    file_path=str(repo_path),
                    stage="license",
                    status="success",
                    metadata=metadata
                )
            else:
                # Quarantine non-compliant repository
                quarantine_path = self.quarantine_dir / repo_path.name
                if quarantine_path.exists():
                    shutil.rmtree(quarantine_path)
                shutil.move(str(repo_path), str(quarantine_path))
                
                results["non_compliant"].append(str(repo_path))
                results["quarantined"].append(str(quarantine_path))
                
                self.logger.log_entry(
                    file_path=str(quarantine_path),
                    stage="license",
                    status="quarantined",
                    metadata=metadata
                )
        
        print(f"✅ License scan complete: {len(results['compliant'])} compliant, "
              f"{len(results['non_compliant'])} quarantined")
        
        return results
