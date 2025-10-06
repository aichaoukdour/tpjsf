from __future__ import annotations

import json
import os
from typing import List

from .config import Config


# Dummy license scanner: mark everything as MIT for prototype
ALLOWED_DEFAULT = {"MIT", "Apache-2.0", "BSD-3-Clause"}


def run(cfg: Config) -> dict:
    discovery_summary = os.path.join(cfg.reports_dir, "discovery.csv")
    # For a prototype, just scan files under raw_dir
    decisions: List[dict] = []
    for root, _dirs, files in os.walk(cfg.raw_dir):
        for name in files:
            src_path = os.path.join(root, name)
            decision = {
                "path": src_path,
                "declared": "MIT",
                "allowed": True,
                "reason": "dummy-scan",
            }
            decisions.append(decision)

    out_path = os.path.join(cfg.reports_dir, "license_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2)

    return {"status": "ok", "report": out_path, "denied": 0}
