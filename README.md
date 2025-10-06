# 🔐 Secure Data Curation Pipeline for Python Code

A modular, secure-by-default pipeline for preparing clean, validated datasets for LLM fine-tuning or RAG (Retrieval-Augmented Generation).

## 🎯 Goals

This pipeline provides:

- **Reproducible**: Same configuration → same output
- **Secure**: Automated license, security, and malware scanning
- **Modular**: Easy to extend with new task branches
- **Auditable**: Complete provenance logging for all files
- **Schema-validated**: Consistent output format

## 📁 Repository Structure

```
code-curation/
├── pipeline/                    # Core pipeline modules
│   ├── __init__.py
│   ├── cli.py                  # CLI orchestrator
│   ├── config.py               # Configuration management
│   ├── discover.py             # Repository discovery
│   ├── license.py              # License scanning
│   ├── security.py             # Security scanning
│   ├── clean.py                # Cleaning & deduplication
│   ├── log.py                  # Provenance logging
│   ├── branch_codegen.py       # Code generation task branch
│   ├── transform.py            # Schema transformation
│   ├── finalize.py             # Output finalization
│   └── metrics.py              # Metrics computation
├── configs/
│   └── default.yaml            # Default configuration
├── schemas/
│   └── common.schema.json      # Output schema definition
├── data/
│   ├── sample_code/            # Sample test data
│   ├── raw/                    # Discovered repositories
│   ├── quarantine/             # Failed security/license checks
│   └── curated/                # Final outputs
│       ├── ft/v1/              # Fine-tuning format
│       └── rag/v1/             # RAG format
├── reports/                    # Pipeline reports
│   ├── discovery.csv
│   ├── provenance.jsonl
│   └── metrics.json
├── Makefile                    # Convenience commands
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
make install
# or manually:
pip install pyyaml
```

### 2. Run the Pipeline

```bash
# Using make
make run

# Or directly with Python
python -m pipeline.cli run --config configs/default.yaml
```

### 3. Check Outputs

```bash
# View curated data for fine-tuning
cat data/curated/ft/v1/train.jsonl

# View curated data for RAG
cat data/curated/rag/v1/train.jsonl

# View metrics
cat reports/metrics.json

# View provenance log
cat reports/provenance.jsonl
```

## ⚙️ Configuration

Edit `configs/default.yaml` to customize the pipeline:

```yaml
# Discovery
discovery_mode: local           # local, github, or url
discovery_sources:
  - data/sample_code
max_repos: 10

# License filtering
allowed_licenses:
  - MIT
  - Apache-2.0
  - BSD-3-Clause
license_strict: false

# Security checks
security_checks:
  - bandit
  - secrets
  - malware
bandit_severity: medium

# Task branch
task_branch: codegen           # codegen, debugging, refactor, docs

# Output formats
output_formats:
  - ft                          # Fine-tuning
  - rag                         # RAG

# Data splits
train_split: 0.8
val_split: 0.1
test_split: 0.1
```

## 🔧 Pipeline Stages

### 1. Discovery
- Finds Python repositories from local directories, GitHub, or URLs
- Copies to `data/raw/`
- Generates `reports/discovery.csv`

### 2. License Validation
- Scans for license compliance
- Quarantines non-compliant repos to `data/quarantine/license/`

### 3. Security Scanning
- Detects secrets, vulnerabilities, and malware patterns
- Quarantines unsafe files to `data/quarantine/security/`

### 4. Cleaning & Deduplication
- Removes test files, vendor code
- Deduplicates by content hash
- Validates code syntax

### 5. Task Branch Extraction
Currently implemented:
- **codegen**: Extracts function signatures, docstrings, and bodies

Planned:
- **debugging**: Extract bug-fix pairs
- **refactor**: Extract refactoring examples
- **docs**: Extract code-documentation pairs

### 6. Schema Transformation
- Transforms to common JSON schema
- Validates against `schemas/common.schema.json`

### 7. Finalization
- Splits into train/val/test
- Outputs to `data/curated/{ft|rag}/v1/`

## 📊 Output Formats

### Fine-Tuning Format (`ft`)
```json
{
  "instruction": "Complete the following code_generation task:",
  "input": "def calculate_average(numbers):\n    \"\"\"Calculate the average...\"\"\"\n",
  "output": "    if not numbers:\n        return 0\n    return sum(numbers) / len(numbers)",
  "metadata": {...}
}
```

### RAG Format (`rag`)
```json
{
  "id": "utils_calculate_average_5",
  "content": "# Code Generation\n\n## Input\ndef calculate_average...\n\n## Output\n...",
  "metadata": {...}
}
```

## 📝 Provenance Logging

All file operations are logged to `reports/provenance.jsonl`:

```json
{
  "timestamp": "2025-10-06T12:00:00.000000",
  "file_path": "data/raw/sample_code/utils.py",
  "file_hash": "abc123...",
  "stage": "security",
  "status": "success",
  "metadata": {"findings_count": 0}
}
```

## 🧪 Adding Your Own Data

### Local Directory
1. Place Python code in any directory
2. Update `configs/default.yaml`:
   ```yaml
   discovery_mode: local
   discovery_sources:
     - /path/to/your/code
   ```

### GitHub Repository (Placeholder)
```yaml
discovery_mode: github
discovery_sources:
  - owner/repo
```

### URL Download (Placeholder)
```yaml
discovery_mode: url
discovery_sources:
  - https://example.com/repo.zip
```

## 🔨 Development

### Clean Generated Files
```bash
make clean
```

### Extend with New Task Branch

1. Create `pipeline/branch_yourtask.py`:
```python
class YourTaskExtractor:
    def extract_all(self, raw_dir: Path) -> List[Dict[str, Any]]:
        # Your extraction logic
        pass
```

2. Add transformer in `pipeline/transform.py`:
```python
def transform_yourtask(self, example: Dict[str, Any]) -> Dict[str, Any]:
    # Your transformation logic
    pass
```

3. Update `pipeline/cli.py` to use your extractor

## 📦 Example Run Output

```
======================================================================
🚀 SECURE DATA CURATION PIPELINE
======================================================================
📋 Configuration loaded from configs/default.yaml
📁 Data directory: data
📊 Reports directory: reports
🎯 Task branch: codegen

──────────────────────────────────────────────────────────────────────
STEP 1: DISCOVERY
──────────────────────────────────────────────────────────────────────
🔍 Discovering repositories (mode: local)...
✅ Discovered 1 repositories
📝 Discovery report saved to reports/discovery.csv

──────────────────────────────────────────────────────────────────────
STEP 2: LICENSE VALIDATION
──────────────────────────────────────────────────────────────────────
📜 Scanning licenses...
✅ License scan complete: 1 compliant, 0 quarantined

──────────────────────────────────────────────────────────────────────
STEP 3: SECURITY SCANNING
──────────────────────────────────────────────────────────────────────
🔒 Scanning for security issues...
✅ Security scan complete: 3 safe files, 0 quarantined

──────────────────────────────────────────────────────────────────────
STEP 4: CLEANING & DEDUPLICATION
──────────────────────────────────────────────────────────────────────
🧹 Cleaning and deduplicating files...
✅ Cleaning complete: 3 files kept, 0 duplicates removed

──────────────────────────────────────────────────────────────────────
STEP 5: TASK BRANCH - CODEGEN
──────────────────────────────────────────────────────────────────────
🔧 Extracting code generation examples...
✅ Extracted 12 code generation examples from 3 files

──────────────────────────────────────────────────────────────────────
STEP 6: SCHEMA TRANSFORMATION
──────────────────────────────────────────────────────────────────────
🔄 Transforming 12 examples to common schema...
✅ Transformed 12 records

──────────────────────────────────────────────────────────────────────
STEP 7: FINALIZATION & OUTPUT
──────────────────────────────────────────────────────────────────────
🎁 Finalizing outputs...
📊 Split data: train=9, val=1, test=2

📦 Packaging FT outputs:
  💾 Saved 9 records to data/curated/ft/v1/train.jsonl
  💾 Saved 1 records to data/curated/ft/v1/val.jsonl
  💾 Saved 2 records to data/curated/ft/v1/test.jsonl

📦 Packaging RAG outputs:
  💾 Saved 9 records to data/curated/rag/v1/train.jsonl
  💾 Saved 1 records to data/curated/rag/v1/val.jsonl
  💾 Saved 2 records to data/curated/rag/v1/test.jsonl

✅ Finalization complete
✅ Metrics saved to reports/metrics.json

======================================================================
📊 PIPELINE SUMMARY
======================================================================

DISCOVERY:
  • total_repos_discovered: 1
  • total_files_discovered: 3

LICENSE:
  • compliant_repos: 1
  • quarantined_repos: 0

SECURITY:
  • total_quarantined: 0

CLEANING:
  • files_before_dedup: 3
  • files_after_dedup: 3
  • duplicates_removed: 0
  • dedup_ratio_percent: 0.0

EXTRACTION:
  • total_examples: 12

TRANSFORM:
  • transformed_records: 12

OUTPUT:
  • train_records: 9
  • val_records: 1
  • test_records: 2
  • total_records: 12

📝 PROVENANCE LOG STATISTICS:
  • Total log entries: 52
  • Unique files processed: 8

✅ PIPELINE COMPLETED SUCCESSFULLY!
======================================================================
```

## 🔐 Security Features

- **Secrets Detection**: Identifies hardcoded passwords, API keys, tokens
- **Vulnerability Scanning**: Flags unsafe patterns (eval, exec, pickle.loads)
- **Malware Checks**: Simple keyword-based detection
- **Fail-Closed**: Quarantines suspicious files by default

## 📈 Metrics & Reporting

The pipeline generates comprehensive metrics in `reports/metrics.json`:

- Discovery statistics
- License compliance rates
- Security findings
- Deduplication ratios
- Output record counts

## 🛠️ Extending the Pipeline

### Add New Security Checks
Edit `pipeline/security.py` to add patterns or integrate tools like:
- `bandit` (static analysis)
- `truffleHog` (secrets scanning)
- `semgrep` (semantic analysis)

### Add New Task Branches
1. Create extractor in `pipeline/branch_*.py`
2. Add transformer method in `pipeline/transform.py`
3. Update CLI orchestrator

### Custom Output Formats
Modify `pipeline/finalize.py` to add new format methods

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a prototype pipeline. Contributions welcome for:
- Additional task branches
- Enhanced security scanning
- GitHub/URL discovery implementation
- Test coverage
- Documentation improvements

## ⚠️ Current Limitations

- GitHub and URL discovery are placeholder implementations
- Security scanning uses simplified regex patterns (not production-grade)
- License detection is keyword-based (use scancode-toolkit for production)
- No actual code formatting (would use black/isort in production)

For production use, integrate:
- `scancode-toolkit` for license scanning
- `bandit` for Python security analysis
- `truffleHog` for secret detection
- `black` and `isort` for code formatting
- `PyGithub` for GitHub API access
