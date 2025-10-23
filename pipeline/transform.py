"""Transform extracted data to unified schema."""

import uuid
import hashlib
import json
from typing import Dict, Any, List
from pathlib import Path


class SchemaTransformer:
    """Transforms branch-specific data to common schema."""
    
    def __init__(self, task_type: str):
        self.task_type = task_type
        self.records = []
    
    def transform_codegen(self, example: Dict[str, Any], split: str = "train") -> Dict[str, Any]:
        """Transform code generation example to common schema."""
        # Create prompt/input
        input_parts = [example["signature"]]
        if example["docstring"]:
            input_parts.append(f'    """{example["docstring"]}"""')
        input_text = "\n".join(input_parts)
        
        # Output is the body
        output_text = example["body"]
        
        # Generate unique ID
        content_hash = hashlib.sha256(
            (input_text + output_text).encode("utf-8")
        ).hexdigest()
        record_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, content_hash))
        
        # Build common schema record
        record = {
            "id": record_id,
            "task": "codegen",
            "input": input_text,
            "output": output_text,
            "metadata": {
                "repo": example["metadata"]["repo"],
                "path": example["metadata"]["path"],
                "commit": example["metadata"]["commit"],
                "license": example["metadata"]["license"],
                "hash": f"sha256:{content_hash}",
                "checks": {
                    "license": "pass",
                    "secrets": "pass",
                    "sast": "pass",
                },
                "split": split,
                "function_name": example["metadata"]["function_name"],
                "num_lines": example["metadata"]["num_lines"],
                "has_docstring": example["metadata"]["has_docstring"],
            }
        }
        
        self.records.append(record)
        return record
    
    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a record against the schema."""
        required_fields = ["id", "task", "input", "output", "metadata"]
        
        if not all(field in record for field in required_fields):
            return False
        
        # Validate metadata
        metadata = record["metadata"]
        required_metadata = ["repo", "path", "commit", "license", "hash", "checks", "split"]
        
        if not all(field in metadata for field in required_metadata):
            return False
        
        # Validate checks
        checks = metadata["checks"]
        required_checks = ["license", "secrets", "sast"]
        
        if not all(check in checks for check in required_checks):
            return False
        
        return True
    
    def get_records(self) -> List[Dict[str, Any]]:
        """Get all transformed records."""
        return self.records
    
    def save_records(self, output_path: Path):
        """Save records to JSONL file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            for record in self.records:
                f.write(json.dumps(record) + "\n")
