"""Code generation task branch - extracts (signature, docstring, body) tuples."""

import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


class CodeGenExtractor:
    """Extracts code generation examples from Python files."""
    
    def __init__(self, min_function_lines: int = 3, require_docstring: bool = False):
        self.min_function_lines = min_function_lines
        self.require_docstring = require_docstring
        self.examples = []
    
    def extract_from_file(self, file_path: Path, content: str, repo_name: str, 
                         commit_sha: str, license: str) -> List[Dict[str, Any]]:
        """Extract code generation examples from a Python file."""
        examples = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                example = self._extract_function(node, content, file_path, repo_name, 
                                                commit_sha, license)
                if example:
                    examples.append(example)
        
        self.examples.extend(examples)
        return examples
    
    def _extract_function(self, node: ast.FunctionDef, content: str, file_path: Path,
                         repo_name: str, commit_sha: str, license: str) -> Optional[Dict[str, Any]]:
        """Extract a single function as a code generation example."""
        # Get function lines
        func_start = node.lineno - 1
        func_end = node.end_lineno if hasattr(node, 'end_lineno') else func_start + 1
        
        func_lines = content.split("\n")[func_start:func_end]
        
        # Skip if too short
        if len(func_lines) < self.min_function_lines:
            return None
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Skip if docstring required but not present
        if self.require_docstring and not docstring:
            return None
        
        # Get function signature
        signature = self._build_signature(node)
        
        # Get function body (without docstring)
        body = self._extract_body(node, func_lines, docstring)
        
        # Skip if body is empty
        if not body.strip():
            return None
        
        # Build the example
        example = {
            "signature": signature,
            "docstring": docstring or "",
            "body": body,
            "full_function": "\n".join(func_lines),
            "metadata": {
                "repo": repo_name,
                "path": str(file_path),
                "commit": commit_sha,
                "license": license,
                "function_name": node.name,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "num_lines": len(func_lines),
                "has_docstring": docstring is not None,
            }
        }
        
        return example
    
    def _build_signature(self, node: ast.FunctionDef) -> str:
        """Build function signature string."""
        args_list = []
        
        # Regular arguments
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args_list.append(arg_str)
        
        # *args
        if node.args.vararg:
            args_list.append(f"*{node.args.vararg.arg}")
        
        # **kwargs
        if node.args.kwarg:
            args_list.append(f"**{node.args.kwarg.arg}")
        
        args_str = ", ".join(args_list)
        
        # Return type
        return_type = ""
        if node.returns:
            return_type = f" -> {ast.unparse(node.returns)}"
        
        prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
        return f"{prefix}def {node.name}({args_str}){return_type}:"
    
    def _extract_body(self, node: ast.FunctionDef, func_lines: List[str], 
                     docstring: Optional[str]) -> str:
        """Extract function body, excluding the signature and docstring."""
        # Start from line 1 (after signature)
        body_lines = func_lines[1:]
        
        if docstring:
            # Find and remove docstring lines
            docstring_found = False
            filtered_lines = []
            
            for line in body_lines:
                stripped = line.strip()
                
                # Skip docstring lines
                if '"""' in stripped or "'''" in stripped:
                    if not docstring_found:
                        docstring_found = True
                        # Skip until closing quotes
                        if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                            continue
                    else:
                        docstring_found = False
                        continue
                
                if not docstring_found:
                    filtered_lines.append(line)
            
            body_lines = filtered_lines
        
        return "\n".join(body_lines).strip()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about extracted examples."""
        if not self.examples:
            return {
                "total_examples": 0,
                "with_docstring": 0,
                "avg_function_length": 0,
                "async_functions": 0,
            }
        
        return {
            "total_examples": len(self.examples),
            "with_docstring": sum(1 for ex in self.examples if ex["metadata"]["has_docstring"]),
            "avg_function_length": sum(ex["metadata"]["num_lines"] for ex in self.examples) / len(self.examples),
            "async_functions": sum(1 for ex in self.examples if ex["metadata"]["is_async"]),
        }
    
    def format_for_instruction_tuning(self, example: Dict[str, Any]) -> Dict[str, str]:
        """Format example for instruction-based fine-tuning."""
        # Create instruction
        instruction = "Generate a Python function"
        if example["docstring"]:
            instruction += " based on the following description"
        
        # Create input (signature + docstring)
        input_parts = [example["signature"]]
        if example["docstring"]:
            input_parts.append(f'    """{example["docstring"]}"""')
        input_text = "\n".join(input_parts)
        
        # Output is the body
        output_text = example["body"]
        
        return {
            "instruction": instruction,
            "input": input_text,
            "output": output_text,
        }
