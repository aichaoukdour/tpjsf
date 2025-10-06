from __future__ import annotations

import json
import os
import random
from typing import List, Dict

from .config import Config


def _split(records: List[Dict[str, object]], seed: int) -> Dict[str, List[Dict[str, object]]]:
    rng = random.Random(seed)
    rng.shuffle(records)
    n = len(records)
    n_train = int(0.8 * n)
    n_val = int(0.1 * n)
    train = records[:n_train]
    val = records[n_train:n_train + n_val]
    test = records[n_train + n_val:]
    return {"train": train, "val": val, "test": test}


def run(cfg: Config) -> dict:
    records_path = os.path.join(cfg.reports_dir, "transformed.jsonl")
    if not os.path.exists(records_path):
        return {"status": "error", "error": "missing transformed records"}

    records: List[Dict[str, object]] = []
    with open(records_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except Exception:
                continue

    splits = _split(records, cfg.seed)

    out_base = os.path.join(cfg.curated_dir, "ft", "v1")
    os.makedirs(out_base, exist_ok=True)

    for split_name, recs in splits.items():
        out_path = os.path.join(out_base, f"{split_name}.jsonl")
        with open(out_path, "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")

    return {"status": "ok", "output_dir": out_base, "counts": {k: len(v) for k, v in splits.items()}}
