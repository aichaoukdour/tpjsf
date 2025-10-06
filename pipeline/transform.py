"""
Transformation module.
Transforms extracted data to a common schema for downstream use.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class SchemaTransformer:
    """Transforms data to a common schema."""
    
    def __init__(self, config, logger):
        """
        Initialize schema transformer.
        
        Args:
            config: PipelineConfig instance
            logger: ProvenanceLogger instance
        """
        self.config = config
        self.logger = logger
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the common schema definition."""
        schema_path = Path(self.config.schema_path)
        
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                return json.load(f)
        
        # Return default schema if file doesn't exist
        return {
            "type": "object",
            "required": ["id", "task", "input", "output", "metadata"],
            "properties": {
                "id": {"type": "string"},
                "task": {"type": "string"},
                "input": {"type": "string"},
                "output": {"type": "string"},
                "metadata": {"type": "object"}
            }
        }
    
    def transform_codegen(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a code generation example to common schema.
        
        Args:
            example: Raw extraction from branch_codegen
            
        Returns:
            Transformed record matching common schema
        """
        # Create a unique ID
        record_id = f"{Path(example['file_path']).stem}_{example['function_name']}_{example['line_start']}"
        
        # Build input (signature + docstring)
        input_text = f"{example['signature']}:\n"
        if example['docstring']:
            input_text += f'    """{example["docstring"]}"""\n'
        
        # Output is the function body
        output_text = example['body']
        
        # Metadata
        metadata = {
            "source_file": example['file_path'],
            "function_name": example['function_name'],
            "line_start": example['line_start'],
            "line_end": example['line_end'],
            "has_docstring": bool(example['docstring']),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return {
            "id": record_id,
            "task": "code_generation",
            "input": input_text,
            "output": output_text,
            "metadata": metadata,
        }
    
    def transform_debugging(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """Transform debugging example (placeholder)."""
        # Placeholder for debugging task branch
        return {
            "id": f"debug_{example.get('id', 'unknown')}",
            "task": "debugging",
            "input": example.get("buggy_code", ""),
            "output": example.get("fixed_code", ""),
            "metadata": example.get("metadata", {}),
        }
    
    def transform_refactor(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """Transform refactoring example (placeholder)."""
        # Placeholder for refactoring task branch
        return {
            "id": f"refactor_{example.get('id', 'unknown')}",
            "task": "refactoring",
            "input": example.get("original_code", ""),
            "output": example.get("refactored_code", ""),
            "metadata": example.get("metadata", {}),
        }
    
    def transform_docs(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """Transform documentation example (placeholder)."""
        # Placeholder for documentation task branch
        return {
            "id": f"docs_{example.get('id', 'unknown')}",
            "task": "documentation",
            "input": example.get("code", ""),
            "output": example.get("documentation", ""),
            "metadata": example.get("metadata", {}),
        }
    
    def transform_all(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform all examples to common schema.
        
        Args:
            examples: List of raw examples
            
        Returns:
            List of transformed records
        """
        print(f"🔄 Transforming {len(examples)} examples to common schema...")
        
        transformed = []
        
        for example in examples:
            try:
                if self.config.task_branch == "codegen":
                    record = self.transform_codegen(example)
                elif self.config.task_branch == "debugging":
                    record = self.transform_debugging(example)
                elif self.config.task_branch == "refactor":
                    record = self.transform_refactor(example)
                elif self.config.task_branch == "docs":
                    record = self.transform_docs(example)
                else:
                    raise ValueError(f"Unknown task branch: {self.config.task_branch}")
                
                transformed.append(record)
                
            except Exception as e:
                self.logger.log_entry(
                    file_path=example.get('file_path', 'unknown'),
                    stage="transform",
                    status="failed",
                    metadata={"error": str(e)}
                )
        
        print(f"✅ Transformed {len(transformed)} records")
        
        return transformed
    
    def validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate a record against the schema.
        
        Simple validation - in production would use jsonschema library.
        
        Args:
            record: Record to validate
            
        Returns:
            True if valid
        """
        required_fields = ["id", "task", "input", "output", "metadata"]
        
        for field in required_fields:
            if field not in record:
                return False
        
        return True
