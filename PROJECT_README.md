# Secure Data Curation Pipeline for Python Code

A production-ready, reproducible pipeline for collecting, validating, cleaning, and preparing Python code datasets for machine learning applications (Fine-Tuning or RAG).

## 🎯 Overview

This pipeline implements a secure-by-default approach to curating Python code from GitHub repositories. It enforces license compliance, security checks, and produces high-quality datasets with full audit trails.

### Key Features

- ✅ **Reproducible**: Same config → same output
- 🔒 **Secure**: License validation, secrets detection, SAST checks
- 📊 **Auditable**: Complete provenance logs for all decisions
- 🎨 **Task-specific**: Supports code generation (extensible to debugging, refactoring, docs)
- 📦 **Schema-validated**: All outputs conform to JSON schemas
- 🚀 **Production-ready**: Deterministic splits, versioning, metrics

## 📁 Project Structure

```
code-curation/
├── pipeline/              # Core pipeline modules
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration management
│   ├── discover.py       # GitHub repository discovery
│   ├── license.py        # License compliance checking
│   ├── security.py       # Security scanning (SAST, secrets, malware)
│   ├── clean.py          # Data cleaning & deduplication
│   ├── branch_codegen.py # Code generation task extraction
│   ├── transform.py      # Schema transformation
│   ├── finalize.py       # Dataset splitting & packaging
│   ├── metrics.py        # Metrics collection & reporting
│   └── log.py           # Provenance & audit logging
├── configs/              # Configuration files
│   ├── default.yaml     # Default configuration
│   └── tiny.yaml        # Quick test configuration
├── schemas/              # JSON schemas
│   ├── common.schema.json
│   └── codegen.schema.json
├── tests/                # Unit tests
├── data/                 # Data storage
│   ├── raw/             # Downloaded repositories
│   ├── quarantine/      # Failed compliance checks
│   └── curated/         # Final outputs
│       ├── ft/          # Fine-tuning format
│       └── rag/         # RAG format
├── reports/              # Audit logs & metrics
│   ├── discovery.csv
│   ├── quarantine.csv
│   ├── provenance.jsonl
│   ├── metrics.json
│   └── MANIFEST.yaml
├── Makefile              # Common commands
└── requirements.txt      # Dependencies
```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
make install

# Or manually
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run full pipeline with default config
make run

# Or use Python directly
python -m pipeline.cli run --config configs/default.yaml

# Quick test with tiny config (2 repos)
make run-tiny
```

### Configuration

Edit `configs/default.yaml` to customize:

```yaml
run_id: "trial-001"

sources:
  github:
    query: "language:Python stars:>100"
    max_repos: 20

compliance:
  license_allow:
    - "MIT"
    - "BSD"
    - "Apache-2.0"

security:
  enable_sast: true
  enable_secrets: true
  enable_malware: true

cleaning:
  drop_tests: true
  max_file_mb: 1.0
  dedupe_level: "function"

branch: "codegen"  # Task type

output:
  type: "finetune"  # or "rag"
  version: "v1"
```

## 🔧 Pipeline Stages

### 1. Discovery & Fetching
- Searches GitHub for repositories matching query
- Clones repos to `data/raw/`
- Logs metadata in `reports/discovery.csv`

### 2. License & Security Gating
- **License Check**: Validates against allowlist
- **Security Scan**: 
  - Secrets detection (API keys, passwords)
  - SAST (eval, exec, command injection)
  - Malware indicators
- Failed items → `data/quarantine/`

### 3. Cleaning & Provenance
- Removes test files, vendor code
- Deduplicates at file or function level
- Tracks all decisions in `reports/provenance.jsonl`

### 4. Task-Specific Extraction
Currently supports **Code Generation**:
- Extracts functions with signatures, docstrings, bodies
- Quality filtering (min length, require docstrings)
- Future: debugging, refactoring, documentation

### 5. Schema Transformation
Converts to unified schema:
```json
{
  "id": "uuid",
  "task": "codegen",
  "input": "def add(a, b):\n    \"\"\"Add two numbers.\"\"\"",
  "output": "    return a + b",
  "metadata": {
    "repo": "owner/name",
    "license": "MIT",
    "checks": {"license": "pass", "secrets": "pass", "sast": "pass"},
    "split": "train"
  }
}
```

### 6. Output Formatting

**Fine-Tuning Format** (`data/curated/ft/v1/`):
- `train.jsonl`, `val.jsonl`, `test.jsonl`
- Default splits: 80/10/10
- Includes MANIFEST.yaml

**RAG Format** (`data/curated/rag/v1/`):
- `chunks.jsonl` (searchable code snippets)
- Optional: embeddings, vector index

### 7. Finalization & Metrics
- Deterministic splits (seeded)
- Version tagging
- Comprehensive metrics in `reports/metrics.json`

## 📊 Outputs

### Reports
- `discovery.csv`: All fetched repositories
- `quarantine.csv`: Rejected files with reasons
- `provenance.jsonl`: Complete audit trail
- `metrics.json`: Pipeline statistics

### Datasets
- `data/curated/ft/v1/`: Fine-tuning ready
- `data/curated/rag/v1/`: RAG ready

### Example Metrics
```json
{
  "discovery": {
    "repos_cloned": 18,
    "repos_found": 20
  },
  "compliance": {
    "files_scanned": 2500,
    "license_passed": 18,
    "quarantined": 125
  },
  "extraction": {
    "examples_extracted": 5234,
    "with_docstring": 3456
  },
  "output": {
    "splits": {
      "train": 4187,
      "val": 523,
      "test": 524
    }
  }
}
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_license.py -v

# Run with coverage
pytest --cov=pipeline tests/
```

## 🎨 Code Quality

```bash
# Format code
make fmt

# Run linters
make lint
```

## 🔐 Security Notes

1. **GitHub Token**: Set `GITHUB_TOKEN` env var for higher API rate limits
2. **Fail-Closed**: Any check error → quarantine (safe default)
3. **No Secrets**: Never commit tokens/keys to config files
4. **Audit Trail**: Every decision is logged

## 📈 Success Criteria

✅ **Reproducibility**: Same config produces identical outputs  
✅ **Security Gates**: All checks enforced, failures quarantined  
✅ **Audit Trail**: Complete provenance for every file  
✅ **Schema Validation**: 100% of records validate  
✅ **Metrics**: Comprehensive reporting with quality checks

## 🛠️ Development

### Adding a New Task Branch

1. Create `pipeline/branch_<taskname>.py`
2. Implement extractor class
3. Add schema in `schemas/<taskname>.schema.json`
4. Update `cli.py` to handle new branch
5. Add tests in `tests/test_branch_<taskname>.py`

### Configuration Options

See `pipeline/config.py` for all available options.

## 🐛 Troubleshooting

**"No repositories found"**
- Check GitHub API rate limits
- Try broader search query
- Set `GITHUB_TOKEN` environment variable

**"Too many files quarantined"**
- Adjust license allowlist
- Review security patterns in `security.py`
- Check file size limits

**"Low extraction count"**
- Lower quality thresholds
- Adjust min_function_lines
- Disable require_docstring

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit pull request

## 📚 References

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Python AST Module](https://docs.python.org/3/library/ast.html)
- [JSON Schema](https://json-schema.org/)

## 🎯 Next Steps

- [ ] Add more task branches (debugging, refactoring, docs)
- [ ] Implement advanced quality scoring
- [ ] Add RAG demo with vector search
- [ ] Support local dataset ingestion
- [ ] Add parallel processing for speed
- [ ] Create web UI for monitoring

---

Built for Phase 1 of the Cursor-like coding assistant project.
