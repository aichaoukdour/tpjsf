from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

from .config import load_config, ensure_dirs
from . import discover, license as license_mod, security, clean, log as log_mod, branch_codegen, transform, finalize, metrics


STEPS = [
    ("discover", discover.run),
    ("license", license_mod.run),
    ("security", security.run),
    ("clean", clean.run),
    ("log", log_mod.run),
    ("branch", branch_codegen.run),
    ("transform", transform.run),
    ("finalize", finalize.run),
    ("metrics", metrics.run),
]


def run_pipeline(config_path: str) -> int:
    cfg = load_config(config_path)
    ensure_dirs(cfg)

    results: Dict[str, Any] = {}

    for name, func in STEPS:
        try:
            step_result = func(cfg)
            results[name] = step_result
        except Exception as e:  # fail-closed on step error
            results[name] = {"status": "error", "error": str(e)}
            # We still continue to allow partial reports and a deterministic failure
            break

    # Write a top-level run summary
    run_summary_path = os.path.join(cfg.reports_dir, "run_summary.json")
    with open(run_summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=True)

    print(f"Pipeline completed. Summary at: {run_summary_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Secure Python Code Curation Pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run the full pipeline")
    run_p.add_argument("--config", required=True, help="Path to YAML/JSON config")

    args = parser.parse_args(argv)

    if args.command == "run":
        return run_pipeline(args.config)

    return 1


if __name__ == "__main__":
    sys.exit(main())
