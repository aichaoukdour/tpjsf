from __future__ import annotations

import json
import os
from typing import Dict, List

from .config import Config


# Common JSON schema target (prototype):
# {
#   "id": str,
#   "source_path": str,
#   "task": "codegen",
#   "input": {"signature": str, "docstring": str|null},
#   "output": {"body": str}
# }


def run(cfg: Config) -> dict:
    branch_path = os.path.join(cfg.reports_dir, "branch_codegen.json")
    if not os.path.exists(branch_path):
        return {"status": "error", "error": "missing branch output"}

    with open(branch_path, "r", encoding="utf-8") as f:
        items: List[Dict[str, object]] = json.load(f)

    transformed: List[Dict[str, object]] = []
    for i, it in enumerate(items):
        rec = {
            "id": f"codegen-{i}",
            "source_path": it.get("file"),
            "task": "codegen",
            "input": {
                "signature": it.get("signature"),
                "docstring": it.get("docstring"),
            },
            "output": {"body": it.get("body")},
        }
        transformed.append(rec)

    out_path = os.path.join(cfg.reports_dir, "transformed.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for rec in transformed:
            f.write(json.dumps(rec) + "\n")

    return {"status": "ok", "count": len(transformed), "records_path": out_path}
