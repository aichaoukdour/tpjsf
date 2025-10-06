from __future__ import annotations

import json
import os
from typing import List

from .config import Config


# Dummy security scan: flags files containing the word "SECRET" or "MALWARE"

def run(cfg: Config) -> dict:
    results: List[dict] = []
    quarantined = 0

    for root, _dirs, files in os.walk(cfg.raw_dir):
        for name in files:
            src_path = os.path.join(root, name)
            try:
                with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                content = ""

            flagged = ("SECRET" in content) or ("MALWARE" in content)
            if flagged:
                # move to quarantine (fail-closed)
                rel = os.path.relpath(src_path, cfg.raw_dir)
                dst_path = os.path.join(cfg.quarantine_dir, rel)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                try:
                    with open(dst_path, "w", encoding="utf-8") as out:
                        out.write(content)
                    os.remove(src_path)
                except Exception:
                    pass
                quarantined += 1

            results.append({
                "path": src_path,
                "flagged": flagged,
                "reason": "contains SECRET/MALWARE token" if flagged else "ok",
            })

    out_path = os.path.join(cfg.reports_dir, "security_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return {"status": "ok", "report": out_path, "quarantined": quarantined}
