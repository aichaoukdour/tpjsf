from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from typing import List

from .config import Config


@dataclass(frozen=True)
class DiscoveryResult:
    repositories: List[str]
    discovery_report_path: str


def run(cfg: Config) -> dict:
    os.makedirs(cfg.raw_dir, exist_ok=True)
    os.makedirs(cfg.reports_dir, exist_ok=True)

    # Minimal prototype: just ensure there is a local sample repo path list
    # In a real implementation, this would clone or copy project sources
    sample_repo_dir = os.path.join(cfg.raw_dir, "sample_repo")
    os.makedirs(sample_repo_dir, exist_ok=True)

    discovery_csv = os.path.join(cfg.reports_dir, "discovery.csv")
    with open(discovery_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["repo", "path", "status"])
        writer.writeheader()
        writer.writerow({"repo": "local-sample", "path": sample_repo_dir, "status": "ok"})

    return {
        "status": "ok",
        "repositories": [sample_repo_dir],
        "discovery_report": discovery_csv,
    }
