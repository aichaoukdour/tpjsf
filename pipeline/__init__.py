"""
Secure Data Curation Pipeline for Python Code

A modular, secure-by-default pipeline for preparing clean, validated datasets
for LLM fine-tuning or RAG.
"""

__version__ = "1.0.0"
__author__ = "Data Curation Pipeline"

from pipeline import config, discover, license, security, clean, log
from pipeline import branch_codegen, transform, finalize, metrics

__all__ = [
    "config",
    "discover",
    "license",
    "security",
    "clean",
    "log",
    "branch_codegen",
    "transform",
    "finalize",
    "metrics",
]
