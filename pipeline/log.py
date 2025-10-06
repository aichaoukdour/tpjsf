from __future__ import annotations

import json
import os
import time
from typing import Dict, Iterable

from .config import Config


def _iter_files(root: str) -> Iterable[str]:
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            yield os.path.join(dirpath, f)


def run(cfg: Config) -> dict:
    out_path = os.path.join(cfg.reports_dir, "provenance.jsonl")
    with open(out_path, "w", encoding="utf-8") as out:
        for fpath in _iter_files(cfg.raw_dir):
            try:
                size = os.path.getsize(fpath)
            except Exception:
                size = None
            record: Dict[str, object] = {
                "timestamp": int(time.time()),
                "path": fpath,
                "size": size,
                "source": "local-sample",
                "stage": "post-clean",
            }
            out.write(json.dumps(record) + "\n")

    return {"status": "ok", "provenance_log": out_path}
