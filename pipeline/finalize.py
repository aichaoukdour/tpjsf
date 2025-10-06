"""
Finalization module.
Splits data into train/val/test and packages outputs for fine-tuning and RAG.
"""

import json
import random
from pathlib import Path
from typing import Dict, Any, List


class OutputFinalizer:
    """Finalizes and packages outputs."""
    
    def __init__(self, config, logger):
        """
        Initialize output finalizer.
        
        Args:
            config: PipelineConfig instance
            logger: ProvenanceLogger instance
        """
        self.config = config
        self.logger = logger
        
        # Set random seed for deterministic splits
        if self.config.deterministic:
            random.seed(self.config.random_seed)
    
    def split_data(self, 
                   records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Split records into train/val/test sets.
        
        Args:
            records: List of transformed records
            
        Returns:
            Dictionary with 'train', 'val', 'test' splits
        """
        # Shuffle for random split
        shuffled = records.copy()
        if self.config.deterministic:
            random.shuffle(shuffled)
        
        total = len(shuffled)
        train_end = int(total * self.config.train_split)
        val_end = train_end + int(total * self.config.val_split)
        
        splits = {
            "train": shuffled[:train_end],
            "val": shuffled[train_end:val_end],
            "test": shuffled[val_end:],
        }
        
        print(f"📊 Split data: train={len(splits['train'])}, "
              f"val={len(splits['val'])}, test={len(splits['test'])}")
        
        return splits
    
    def format_for_finetuning(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a record for fine-tuning (instruction format).
        
        Args:
            record: Transformed record
            
        Returns:
            Fine-tuning formatted record
        """
        # Common instruction-tuning format
        return {
            "instruction": f"Complete the following {record['task']} task:",
            "input": record['input'],
            "output": record['output'],
            "metadata": record['metadata'],
        }
    
    def format_for_rag(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a record for RAG (document format).
        
        Args:
            record: Transformed record
            
        Returns:
            RAG formatted record
        """
        # RAG format with concatenated content
        content = f"# {record['task'].replace('_', ' ').title()}\n\n"
        content += f"## Input\n{record['input']}\n\n"
        content += f"## Output\n{record['output']}\n"
        
        return {
            "id": record['id'],
            "content": content,
            "metadata": {
                **record['metadata'],
                "task": record['task'],
            }
        }
    
    def save_split(self, 
                   records: List[Dict[str, Any]],
                   output_dir: Path,
                   split_name: str,
                   format_type: str):
        """
        Save a data split to disk.
        
        Args:
            records: List of records
            output_dir: Output directory
            split_name: 'train', 'val', or 'test'
            format_type: 'ft' or 'rag'
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{split_name}.jsonl"
        
        with open(output_file, 'w') as f:
            for record in records:
                if format_type == "ft":
                    formatted = self.format_for_finetuning(record)
                elif format_type == "rag":
                    formatted = self.format_for_rag(record)
                else:
                    formatted = record
                
                f.write(json.dumps(formatted) + '\n')
        
        print(f"  💾 Saved {len(records)} records to {output_file}")
    
    def finalize_all(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Finalize all records and save outputs.
        
        Args:
            records: List of transformed records
            
        Returns:
            Dictionary with finalization results
        """
        print(f"🎁 Finalizing outputs...")
        
        # Split data
        splits = self.split_data(records)
        
        results = {
            "total_records": len(records),
            "splits": {k: len(v) for k, v in splits.items()},
            "output_paths": [],
        }
        
        # Save outputs for each format
        for format_type in self.config.output_formats:
            print(f"\n📦 Packaging {format_type.upper()} outputs:")
            
            output_dir = Path(self.config.data_dir) / "curated" / format_type / "v1"
            
            for split_name, split_records in splits.items():
                self.save_split(split_records, output_dir, split_name, format_type)
                results["output_paths"].append(str(output_dir / f"{split_name}.jsonl"))
            
            # Log finalization
            self.logger.log_entry(
                file_path=str(output_dir),
                stage="finalize",
                status="success",
                metadata={
                    "format": format_type,
                    "splits": {k: len(v) for k, v in splits.items()},
                }
            )
        
        print(f"\n✅ Finalization complete")
        
        return results
