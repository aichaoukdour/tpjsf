"""Secure Python Code Curation Pipeline (prototype).

Each module exposes a `run` function that accepts a config dictionary and
returns a structured result for orchestration.
"""

from .config import load_config

__all__ = [
    "load_config",
]
