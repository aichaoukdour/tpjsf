# 🚀 Quick Start Guide

Get the Secure Data Curation Pipeline running in 5 minutes!

## 📦 Installation

```bash
# Clone or navigate to the repository
cd code-curation

# Install dependencies (just PyYAML)
make install
# or manually:
pip install pyyaml
```

## ▶️ Run the Pipeline

```bash
# Run with default configuration
make run

# Or use python directly
python3 -m pipeline.cli run --config configs/default.yaml
```

## 📂 What Gets Created

After running, you'll have:

```
data/
├── raw/                          # Copied source code
│   └── sample_code/
├── curated/                      # Your curated datasets!
│   ├── ft/v1/                   # Fine-tuning format
│   │   ├── train.jsonl
│   │   ├── val.jsonl
│   │   └── test.jsonl
│   └── rag/v1/                  # RAG format
│       ├── train.jsonl
│       ├── val.jsonl
│       └── test.jsonl
└── quarantine/                   # Rejected files
    ├── license/
    └── security/

reports/
├── discovery.csv                 # What was found
├── provenance.jsonl             # Full audit trail
└── metrics.json                 # Pipeline statistics
```

## 🔍 Inspect the Outputs

### View Fine-Tuning Data
```bash
# See one record
head -n 1 data/curated/ft/v1/train.jsonl | python3 -m json.tool

# Count records
wc -l data/curated/ft/v1/*.jsonl
```

Example output:
```json
{
  "instruction": "Complete the following code_generation task:",
  "input": "def is_palindrome(text: str) -> bool:\n    \"\"\"Check if...\"\"\"\n",
  "output": "cleaned = ''.join(c.lower() for c in text if c.isalnum())\n    return cleaned == cleaned[::-1]",
  "metadata": {
    "source_file": "data/raw/sample_code/string_utils.py",
    "function_name": "is_palindrome",
    "has_docstring": true
  }
}
```

### View RAG Data
```bash
head -n 1 data/curated/rag/v1/train.jsonl | python3 -m json.tool
```

### View Metrics
```bash
cat reports/metrics.json | python3 -m json.tool
```

### View Provenance Log
```bash
head -n 10 reports/provenance.jsonl | python3 -m json.tool
```

## 🎛️ Customize for Your Data

### 1. Add Your Python Code

```bash
# Option A: Copy files to sample_code
cp -r /path/to/your/python/project data/sample_code/

# Option B: Update config to point to your code
nano configs/default.yaml
```

Edit `discovery_sources`:
```yaml
discovery_sources:
  - /path/to/your/python/code
  - /another/path
```

### 2. Adjust Settings

```yaml
# In configs/default.yaml

# Filter by license
allowed_licenses:
  - MIT
  - Apache-2.0

# Security strictness
bandit_severity: high  # low, medium, high

# Exclude patterns
exclude_patterns:
  - "*/test/*"
  - "*/vendor/*"

# Data splits
train_split: 0.8
val_split: 0.1
test_split: 0.1
```

### 3. Re-run

```bash
make clean  # Clear previous run
make run    # Run again with new config
```

## 📊 Understanding the Output

### Fine-Tuning Format
Perfect for instruction-tuned models (GPT, Llama, etc.):
- `instruction`: Task description
- `input`: Function signature + docstring
- `output`: Function implementation
- `metadata`: Provenance information

### RAG Format
Perfect for vector databases (Pinecone, Weaviate, etc.):
- `id`: Unique identifier
- `content`: Formatted markdown with input/output
- `metadata`: Rich metadata for filtering

## 🧪 Test with Different Task Branches

Currently implemented: **codegen** (code generation)

Planned:
- `debugging`: Bug-fix pairs
- `refactor`: Refactoring examples
- `docs`: Code-documentation pairs

Change in `configs/default.yaml`:
```yaml
task_branch: codegen  # Change this when other branches are implemented
```

## 🛠️ Common Tasks

### Clean Everything
```bash
make clean
```

### Run with Custom Config
```bash
python3 -m pipeline.cli run --config configs/my_config.yaml
```

### View Help
```bash
python3 -m pipeline.cli --help
```

## 📈 Expected Pipeline Output

```
======================================================================
🚀 SECURE DATA CURATION PIPELINE
======================================================================

STEP 1: DISCOVERY
  ✅ Discovered 1 repositories

STEP 2: LICENSE VALIDATION
  ✅ License scan complete: 1 compliant, 0 quarantined

STEP 3: SECURITY SCANNING
  ✅ Security scan complete: 3 safe files, 0 quarantined

STEP 4: CLEANING & DEDUPLICATION
  ✅ Cleaning complete: 3 files kept, 0 duplicates removed

STEP 5: TASK BRANCH - CODEGEN
  ✅ Extracted 11 code generation examples from 3 files

STEP 6: SCHEMA TRANSFORMATION
  ✅ Transformed 11 records

STEP 7: FINALIZATION & OUTPUT
  💾 Saved 8 records to data/curated/ft/v1/train.jsonl
  💾 Saved 1 records to data/curated/ft/v1/val.jsonl
  💾 Saved 2 records to data/curated/ft/v1/test.jsonl

✅ PIPELINE COMPLETED SUCCESSFULLY!
======================================================================
```

## ❓ Troubleshooting

### "No examples extracted"
- Make sure your Python files have functions with docstrings
- Check that files aren't being excluded by patterns
- Review `reports/provenance.jsonl` for details

### "File quarantined"
- Check `data/quarantine/` directories
- Review security settings in config
- Check license compliance

### "Configuration not found"
- Ensure `configs/default.yaml` exists
- Use `--config` flag with correct path

## 🎯 Next Steps

1. **Add more data**: Point to larger Python repositories
2. **Tune filters**: Adjust exclusion patterns and size limits
3. **Customize schema**: Edit `schemas/common.schema.json`
4. **Extend pipeline**: Add new task branches or output formats
5. **Integrate tools**: Replace placeholders with real security scanners

## 📚 Learn More

- Full documentation: See `README.md`
- Configuration guide: See `configs/default.yaml` comments
- Schema definition: See `schemas/common.schema.json`
- Module documentation: See docstrings in `pipeline/*.py`

Happy curating! 🎉
