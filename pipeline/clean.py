"""
Cleaning and deduplication module.
Removes test files, vendor code, duplicates, and formats code.
"""

import hashlib
from pathlib import Path
from typing import Dict, Any, Set, List
import fnmatch


class CodeCleaner:
    """Cleans and deduplicates Python code files."""
    
    def __init__(self, config, logger):
        """
        Initialize code cleaner.
        
        Args:
            config: PipelineConfig instance
            logger: ProvenanceLogger instance
        """
        self.config = config
        self.logger = logger
        self.seen_hashes: Set[str] = set()
    
    def should_exclude(self, file_path: Path, base_dir: Path) -> bool:
        """
        Check if a file should be excluded based on patterns.
        
        Args:
            file_path: Path to the file
            base_dir: Base directory for relative path matching
            
        Returns:
            True if file should be excluded
        """
        try:
            rel_path = file_path.relative_to(base_dir)
        except ValueError:
            rel_path = file_path
        
        rel_path_str = str(rel_path)
        
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(rel_path_str, pattern):
                return True
            # Also check individual parts
            for part in rel_path.parts:
                if fnmatch.fnmatch(part, pattern.strip('*/')):
                    return True
        
        return False
    
    def is_valid_size(self, file_path: Path) -> bool:
        """Check if file size is within acceptable range."""
        try:
            size = file_path.stat().st_size
            return self.config.min_file_size <= size <= self.config.max_file_size
        except Exception:
            return False
    
    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file content."""
        hasher = hashlib.sha256()
        try:
            content = file_path.read_bytes()
            hasher.update(content)
            return hasher.hexdigest()
        except Exception:
            return None
    
    def is_duplicate(self, file_path: Path) -> bool:
        """
        Check if file is a duplicate based on content hash.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is a duplicate
        """
        file_hash = self.compute_hash(file_path)
        
        if file_hash is None:
            return False
        
        if file_hash in self.seen_hashes:
            return True
        
        self.seen_hashes.add(file_hash)
        return False
    
    def format_code(self, file_path: Path) -> bool:
        """
        Format Python code using black and isort.
        
        This is a placeholder - in production would use actual black/isort.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if formatting succeeded
        """
        if not self.config.format_code:
            return True
        
        try:
            # Placeholder: just verify it's valid Python
            content = file_path.read_text(errors='ignore')
            compile(content, str(file_path), 'exec')
            return True
        except SyntaxError:
            return False
        except Exception:
            return False
    
    def clean_all(self, raw_dir: Path) -> Dict[str, Any]:
        """
        Clean all Python files in the raw directory.
        
        Args:
            raw_dir: Path to raw data directory
            
        Returns:
            Dictionary with cleaning results
        """
        print(f"🧹 Cleaning and deduplicating files...")
        
        results = {
            "total_files": 0,
            "excluded_files": [],
            "invalid_size_files": [],
            "duplicate_files": [],
            "format_failed_files": [],
            "cleaned_files": [],
        }
        
        # Find all Python files
        py_files = list(raw_dir.rglob("*.py"))
        results["total_files"] = len(py_files)
        
        for py_file in py_files:
            # Check exclusion patterns
            if self.should_exclude(py_file, raw_dir):
                results["excluded_files"].append(str(py_file))
                py_file.unlink()
                self.logger.log_entry(
                    file_path=str(py_file),
                    stage="clean",
                    status="excluded",
                    metadata={"reason": "pattern_match"}
                )
                continue
            
            # Check file size
            if not self.is_valid_size(py_file):
                results["invalid_size_files"].append(str(py_file))
                py_file.unlink()
                self.logger.log_entry(
                    file_path=str(py_file),
                    stage="clean",
                    status="excluded",
                    metadata={"reason": "invalid_size"}
                )
                continue
            
            # Check for duplicates
            if self.is_duplicate(py_file):
                results["duplicate_files"].append(str(py_file))
                py_file.unlink()
                self.logger.log_entry(
                    file_path=str(py_file),
                    stage="clean",
                    status="excluded",
                    metadata={"reason": "duplicate"}
                )
                continue
            
            # Format code
            if not self.format_code(py_file):
                results["format_failed_files"].append(str(py_file))
                py_file.unlink()
                self.logger.log_entry(
                    file_path=str(py_file),
                    stage="clean",
                    status="excluded",
                    metadata={"reason": "format_failed"}
                )
                continue
            
            # File is clean
            results["cleaned_files"].append(str(py_file))
            self.logger.log_entry(
                file_path=str(py_file),
                stage="clean",
                status="success",
                metadata={}
            )
        
        print(f"✅ Cleaning complete: {len(results['cleaned_files'])} files kept, "
              f"{len(results['duplicate_files'])} duplicates removed")
        
        return results
