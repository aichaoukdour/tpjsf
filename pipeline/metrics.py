from __future__ import annotations

import json
import os

from .config import Config


def run(cfg: Config) -> dict:
    # Simple prototype metrics based on files present
    license_report = os.path.join(cfg.reports_dir, "license_report.json")
    security_report = os.path.join(cfg.reports_dir, "security_report.json")
    transformed_path = os.path.join(cfg.reports_dir, "transformed.jsonl")

    counts = {"files_scanned": 0, "security_flagged": 0, "records": 0}

    if os.path.exists(license_report):
        try:
            with open(license_report, "r", encoding="utf-8") as f:
                counts["files_scanned"] = len(json.load(f))
        except Exception:
            pass

    if os.path.exists(security_report):
        try:
            with open(security_report, "r", encoding="utf-8") as f:
                data = json.load(f)
                counts["security_flagged"] = sum(1 for x in data if x.get("flagged"))
        except Exception:
            pass

    if os.path.exists(transformed_path):
        try:
            with open(transformed_path, "r", encoding="utf-8") as f:
                counts["records"] = sum(1 for _ in f)
        except Exception:
            pass

    out_path = os.path.join(cfg.reports_dir, "metrics.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(counts, f, indent=2, sort_keys=True)

    return {"status": "ok", "metrics_path": out_path, **counts}
