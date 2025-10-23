"""Finalization, splitting, and packaging of datasets."""

import json
import hashlib
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import yaml


class DatasetFinalizer:
    """Finalizes datasets with splits, versioning, and manifests."""
    
    def __init__(self, train_split: float = 0.8, val_split: float = 0.1, 
                 test_split: float = 0.1, seed: int = 42):
        self.train_split = train_split
        self.val_split = val_split
        self.test_split = test_split
        self.seed = seed
        
        # Validate splits
        assert abs(train_split + val_split + test_split - 1.0) < 0.001, "Splits must sum to 1.0"
    
    def create_splits(self, records: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Create train/val/test splits deterministically."""
        # Use hash-based splitting for determinism
        random.seed(self.seed)
        
        # Shuffle based on IDs (deterministic)
        sorted_records = sorted(records, key=lambda x: x["id"])
        random.shuffle(sorted_records)
        
        n = len(sorted_records)
        train_end = int(n * self.train_split)
        val_end = train_end + int(n * self.val_split)
        
        train = sorted_records[:train_end]
        val = sorted_records[train_end:val_end]
        test = sorted_records[val_end:]
        
        # Update split metadata
        for record in train:
            record["metadata"]["split"] = "train"
        for record in val:
            record["metadata"]["split"] = "val"
        for record in test:
            record["metadata"]["split"] = "test"
        
        return train, val, test
    
    def save_finetune_format(self, records: List[Dict[str, Any]], output_dir: Path, 
                            version: str = "v1"):
        """Save dataset in fine-tuning format."""
        output_path = output_dir / "ft" / version
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create splits
        train, val, test = self.create_splits(records)
        
        # Save splits
        self._save_jsonl(train, output_path / "train.jsonl")
        self._save_jsonl(val, output_path / "val.jsonl")
        self._save_jsonl(test, output_path / "test.jsonl")
        
        # Create manifest
        manifest = self._create_manifest(train, val, test, version, "finetune")
        self._save_manifest(manifest, output_path / "MANIFEST.yaml")
        
        return {
            "train": len(train),
            "val": len(val),
            "test": len(test),
            "output_dir": str(output_path)
        }
    
    def save_rag_format(self, records: List[Dict[str, Any]], output_dir: Path,
                       version: str = "v1"):
        """Save dataset in RAG format."""
        output_path = output_dir / "rag" / version
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create chunks (each record becomes a chunk)
        chunks = []
        for record in records:
            chunk = {
                "id": record["id"],
                "text": f"{record['input']}\n\n{record['output']}",
                "metadata": record["metadata"]
            }
            chunks.append(chunk)
        
        # Save chunks
        self._save_jsonl(chunks, output_path / "chunks.jsonl")
        
        # Create a simple manifest
        manifest = {
            "dataset": "python-curation",
            "version": version,
            "format": "rag",
            "created_at": datetime.utcnow().isoformat(),
            "records": {
                "total": len(chunks),
            },
            "hash": self._compute_dataset_hash(chunks),
        }
        
        self._save_manifest(manifest, output_path / "MANIFEST.yaml")
        
        return {
            "total": len(chunks),
            "output_dir": str(output_path)
        }
    
    def _save_jsonl(self, records: List[Dict[str, Any]], path: Path):
        """Save records as JSONL."""
        with open(path, "w") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
    
    def _create_manifest(self, train: List[Dict], val: List[Dict], test: List[Dict],
                        version: str, format_type: str) -> Dict[str, Any]:
        """Create dataset manifest."""
        all_records = train + val + test
        
        return {
            "dataset": "python-curation",
            "version": version,
            "format": format_type,
            "created_at": datetime.utcnow().isoformat(),
            "records": {
                "train": len(train),
                "val": len(val),
                "test": len(test),
                "total": len(all_records),
            },
            "hash": self._compute_dataset_hash(all_records),
            "splits": {
                "train": self.train_split,
                "val": self.val_split,
                "test": self.test_split,
            },
            "seed": self.seed,
        }
    
    def _save_manifest(self, manifest: Dict[str, Any], path: Path):
        """Save manifest as YAML."""
        with open(path, "w") as f:
            yaml.dump(manifest, f, default_flow_style=False)
    
    def _compute_dataset_hash(self, records: List[Dict[str, Any]]) -> str:
        """Compute deterministic hash of entire dataset."""
        # Sort by ID for determinism
        sorted_records = sorted(records, key=lambda x: x["id"])
        
        # Compute hash
        hasher = hashlib.sha256()
        for record in sorted_records:
            hasher.update(json.dumps(record, sort_keys=True).encode("utf-8"))
        
        return f"sha256:{hasher.hexdigest()}"
