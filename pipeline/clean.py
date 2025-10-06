from __future__ import annotations

import hashlib
import os
import shutil
from typing import Dict, Set

from .config import Config


SKIP_DIRS = {"tests", "test", "__pycache__", "venv", "env", ".venv", "site-packages", "build", "dist"}


def run(cfg: Config) -> dict:
    # Drop test/vendor-like dirs, dedupe by content hash, basic formatting stub
    seen_hashes: Set[str] = set()
    removed = 0
    deduped = 0

    for root, dirs, files in os.walk(cfg.raw_dir, topdown=True):
        # prune dirs in-place
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = os.path.join(root, name)
            try:
                with open(path, "rb") as f:
                    data = f.read()
            except Exception:
                continue
            content_hash = hashlib.sha256(data).hexdigest()
            if content_hash in seen_hashes:
                os.remove(path)
                deduped += 1
                continue
            seen_hashes.add(content_hash)

            # formatting stub: normalize trailing newline for .py files
            if name.endswith(".py"):
                try:
                    text = data.decode("utf-8", errors="ignore")
                    normalized = text.rstrip("\n") + "\n"
                    if normalized != text:
                        with open(path, "w", encoding="utf-8") as out:
                            out.write(normalized)
                except Exception:
                    pass

    return {"status": "ok", "deduped": deduped, "removed": removed}
