"""Data cleaning and deduplication."""

import hashlib
import ast
from pathlib import Path
from typing import Set, Dict, Any, List, Tuple
import os


class DataCleaner:
    """Cleans and deduplicates Python code."""
    
    def __init__(self, drop_tests: bool = True, max_file_mb: float = 1.0, 
                 dedupe_level: str = "function", min_line_length: int = 3,
                 max_line_length: int = 1000):
        self.drop_tests = drop_tests
        self.max_file_bytes = int(max_file_mb * 1024 * 1024)
        self.dedupe_level = dedupe_level
        self.min_line_length = min_line_length
        self.max_line_length = max_line_length
        
        # Track seen hashes for deduplication
        self.seen_hashes: Set[str] = set()
        self.dedup_stats = {"total": 0, "duplicates": 0}
    
    def should_skip_file(self, file_path: Path) -> Tuple[bool, str]:
        """Determine if file should be skipped."""
        # Skip non-Python files
        if file_path.suffix != ".py":
            return True, "Not a Python file"
        
        # Skip test files if configured
        if self.drop_tests:
            path_str = str(file_path).lower()
            if any(test_pattern in path_str for test_pattern in 
                   ["test_", "_test.py", "/tests/", "/test/"]):
                return True, "Test file"
        
        # Skip files that are too large
        try:
            file_size = file_path.stat().st_size
            if file_size > self.max_file_bytes:
                return True, f"File too large ({file_size} bytes)"
        except Exception:
            return True, "Cannot stat file"
        
        # Skip __pycache__ and other common excludes
        path_parts = file_path.parts
        exclude_dirs = {"__pycache__", ".git", ".tox", "venv", "env", "node_modules", "vendor"}
        if any(part in exclude_dirs for part in path_parts):
            return True, "Excluded directory"
        
        return False, ""
    
    def clean_content(self, content: str) -> str:
        """Clean file content."""
        lines = content.split("\n")
        cleaned_lines = []
        
        for line in lines:
            # Strip trailing whitespace
            line = line.rstrip()
            
            # Skip lines that are too short or too long
            if len(line) < self.min_line_length or len(line) > self.max_line_length:
                if line.strip():  # Keep non-empty lines even if short
                    cleaned_lines.append(line)
                continue
            
            cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)
    
    def compute_hash(self, content: str) -> str:
        """Compute content hash for deduplication."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    def is_duplicate(self, content_hash: str) -> bool:
        """Check if content is a duplicate."""
        self.dedup_stats["total"] += 1
        
        if content_hash in self.seen_hashes:
            self.dedup_stats["duplicates"] += 1
            return True
        
        self.seen_hashes.add(content_hash)
        return False
    
    def extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions from Python code."""
        functions = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Get function source
                    func_start = node.lineno - 1
                    func_end = node.end_lineno if hasattr(node, 'end_lineno') else func_start + 1
                    
                    func_lines = content.split("\n")[func_start:func_end]
                    func_code = "\n".join(func_lines)
                    
                    # Extract docstring if present
                    docstring = ast.get_docstring(node) or ""
                    
                    # Get function signature
                    args = [arg.arg for arg in node.args.args]
                    signature = f"{node.name}({', '.join(args)})"
                    
                    functions.append({
                        "name": node.name,
                        "signature": signature,
                        "code": func_code,
                        "docstring": docstring,
                        "start_line": func_start + 1,
                        "end_line": func_end,
                    })
        
        except SyntaxError:
            # If we can't parse, skip function extraction
            pass
        
        return functions
    
    def deduplicate_functions(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate functions based on content hash."""
        unique_functions = []
        
        for func in functions:
            func_hash = self.compute_hash(func["code"])
            if not self.is_duplicate(func_hash):
                func["hash"] = func_hash
                unique_functions.append(func)
        
        return unique_functions
    
    def get_dedup_ratio(self) -> float:
        """Calculate deduplication ratio."""
        if self.dedup_stats["total"] == 0:
            return 0.0
        return self.dedup_stats["duplicates"] / self.dedup_stats["total"]
