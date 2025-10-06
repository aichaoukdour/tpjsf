from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict

import yaml


@dataclass(frozen=True)
class Config:
    data_dir: str
    reports_dir: str
    allowed_licenses: list[str]
    branch: str
    seed: int

    raw_dir: str
    quarantine_dir: str
    curated_dir: str

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Config":
        base_data = d.get("data_dir", "data")
        base_reports = d.get("reports_dir", "reports")
        data_dir = os.path.abspath(base_data)
        reports_dir = os.path.abspath(base_reports)
        return Config(
            data_dir=data_dir,
            reports_dir=reports_dir,
            allowed_licenses=d.get("allowed_licenses", ["MIT", "Apache-2.0", "BSD-3-Clause"]),
            branch=d.get("branch", "codegen"),
            seed=int(d.get("seed", 42)),
            raw_dir=os.path.join(data_dir, "raw"),
            quarantine_dir=os.path.join(data_dir, "quarantine"),
            curated_dir=os.path.join(data_dir, "curated"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_dir": self.data_dir,
            "reports_dir": self.reports_dir,
            "allowed_licenses": self.allowed_licenses,
            "branch": self.branch,
            "seed": self.seed,
            "raw_dir": self.raw_dir,
            "quarantine_dir": self.quarantine_dir,
            "curated_dir": self.curated_dir,
        }


def load_config(path: str) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        if path.endswith(".yaml") or path.endswith(".yml"):
            data = yaml.safe_load(f)
        elif path.endswith(".json"):
            data = json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {path}")
    return Config.from_dict(data or {})


def ensure_dirs(cfg: Config) -> None:
    os.makedirs(cfg.raw_dir, exist_ok=True)
    os.makedirs(cfg.quarantine_dir, exist_ok=True)
    os.makedirs(cfg.curated_dir, exist_ok=True)
    os.makedirs(cfg.reports_dir, exist_ok=True)
