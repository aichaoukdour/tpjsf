"""
Code generation task branch.
Extracts function signatures, docstrings, and bodies for code generation tasks.
"""

import ast
from pathlib import Path
from typing import Dict, Any, List, Optional


class CodeGenExtractor:
    """Extracts code generation examples from Python files."""
    
    def __init__(self, config, logger):
        """
        Initialize code generation extractor.
        
        Args:
            config: PipelineConfig instance
            logger: ProvenanceLogger instance
        """
        self.config = config
        self.logger = logger
    
    def extract_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract function/method examples from a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            List of extraction results
        """
        examples = []
        
        try:
            content = file_path.read_text(errors='ignore')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    example = self._extract_function(node, content, file_path)
                    if example:
                        examples.append(example)
        
        except SyntaxError as e:
            self.logger.log_entry(
                file_path=str(file_path),
                stage="branch_codegen",
                status="failed",
                metadata={"error": "syntax_error", "message": str(e)}
            )
        except Exception as e:
            self.logger.log_entry(
                file_path=str(file_path),
                stage="branch_codegen",
                status="failed",
                metadata={"error": "extraction_error", "message": str(e)}
            )
        
        return examples
    
    def _extract_function(self, 
                         node: ast.FunctionDef,
                         source: str,
                         file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract a single function as a code generation example.
        
        Args:
            node: AST node for the function
            source: Source code of the file
            file_path: Path to the source file
            
        Returns:
            Dictionary with signature, docstring, and body
        """
        try:
            # Get function name
            func_name = node.name
            
            # Get docstring
            docstring = ast.get_docstring(node) or ""
            
            # Get function signature
            args = []
            for arg in node.args.args:
                arg_str = arg.arg
                if arg.annotation:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                args.append(arg_str)
            
            signature = f"def {func_name}({', '.join(args)})"
            
            # Add return type if present
            if node.returns:
                signature += f" -> {ast.unparse(node.returns)}"
            
            # Get function body (excluding docstring)
            body_nodes = node.body
            if (body_nodes and 
                isinstance(body_nodes[0], ast.Expr) and 
                isinstance(body_nodes[0].value, ast.Constant)):
                # Skip docstring node
                body_nodes = body_nodes[1:]
            
            if not body_nodes:
                return None  # Skip functions with only docstring
            
            # Extract body source
            body_lines = source.split('\n')
            start_line = body_nodes[0].lineno - 1
            end_line = body_nodes[-1].end_lineno
            
            body_source = '\n'.join(body_lines[start_line:end_line])
            
            return {
                "file_path": str(file_path),
                "function_name": func_name,
                "signature": signature,
                "docstring": docstring,
                "body": body_source.strip(),
                "line_start": node.lineno,
                "line_end": node.end_lineno,
            }
        
        except Exception as e:
            return None
    
    def extract_all(self, raw_dir: Path) -> List[Dict[str, Any]]:
        """
        Extract code generation examples from all files.
        
        Args:
            raw_dir: Path to raw data directory
            
        Returns:
            List of all extraction results
        """
        print(f"🔧 Extracting code generation examples...")
        
        all_examples = []
        py_files = list(raw_dir.rglob("*.py"))
        
        for py_file in py_files:
            examples = self.extract_from_file(py_file)
            all_examples.extend(examples)
            
            if examples:
                self.logger.log_entry(
                    file_path=str(py_file),
                    stage="branch_codegen",
                    status="success",
                    metadata={"examples_extracted": len(examples)}
                )
        
        print(f"✅ Extracted {len(all_examples)} code generation examples from {len(py_files)} files")
        
        return all_examples
