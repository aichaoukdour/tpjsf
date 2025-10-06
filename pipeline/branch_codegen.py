from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from typing import List, Dict

from .config import Config


@dataclass(frozen=True)
class CodegenRecord:
    file: str
    function_name: str
    signature: str
    docstring: str | None
    body: str


def _extract_functions(py_src: str, file_path: str) -> List[CodegenRecord]:
    records: List[CodegenRecord] = []
    try:
        tree = ast.parse(py_src)
    except SyntaxError:
        return records

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            signature = f"def {node.name}({', '.join(args)}):"
            doc = ast.get_docstring(node)
            # Extract source lines for body (approximate)
            body_lines: List[str] = []
            for stmt in node.body:
                try:
                    src = ast.get_source_segment(py_src, stmt)
                except Exception:
                    src = None
                if src:
                    body_lines.append(src)
            records.append(
                CodegenRecord(
                    file=file_path,
                    function_name=node.name,
                    signature=signature,
                    docstring=doc,
                    body="\n".join(body_lines),
                )
            )
    return records


def run(cfg: Config) -> dict:
    out_items: List[Dict[str, object]] = []
    for dirpath, _dirs, files in os.walk(cfg.raw_dir):
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    src = f.read()
            except Exception:
                continue
            recs = _extract_functions(src, path)
            for r in recs:
                out_items.append({
                    "file": r.file,
                    "function_name": r.function_name,
                    "signature": r.signature,
                    "docstring": r.docstring,
                    "body": r.body,
                })

    out_path = os.path.join(cfg.reports_dir, "branch_codegen.json")
    import json

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_items, f, indent=2)

    return {"status": "ok", "records": len(out_items), "report": out_path}
