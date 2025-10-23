# Quick Reference Guide

## Essential Commands

### Installation
```bash
# Install all dependencies
make install

# Verify installation
python3 verify_installation.py
```

### Running the Pipeline

```bash
# Quick test (2 repos, ~5-10 min)
make run-tiny

# Full run (20 repos, ~15-25 min)
make run

# Custom config
python3 -m pipeline.cli run --config configs/my-config.yaml
```

### Testing

```bash
# Run all tests
make test

# Run specific test
pytest tests/test_license.py -v

# With coverage
pytest --cov=pipeline tests/
```

### Code Quality

```bash
# Format code
make fmt

# Run linters
make lint

# Clean generated files
make clean
```

## File Locations

### Outputs
- **Datasets**: `data/curated/ft/v1/` or `data/curated/rag/v1/`
- **Reports**: `reports/`
  - `discovery.csv` - Fetched repos
  - `quarantine.csv` - Rejected files
  - `provenance.jsonl` - Audit trail
  - `metrics.json` - Statistics

### Inputs
- **Configs**: `configs/default.yaml` or `configs/tiny.yaml`
- **Schemas**: `schemas/*.json`

## Viewing Results

```bash
# View metrics
cat reports/metrics.json | python3 -m json.tool

# View first training example
head -n 1 data/curated/ft/v1/train.jsonl | python3 -m json.tool

# Count examples
wc -l data/curated/ft/v1/*.jsonl

# View quarantined files
cat reports/quarantine.csv

# Search provenance log
grep '"status":"kept"' reports/provenance.jsonl | wc -l
```

## Common Configuration Changes

### Change number of repos
```yaml
# Edit configs/default.yaml
sources:
  github:
    max_repos: 50  # Change from 20
```

### Add allowed license
```yaml
# Edit configs/default.yaml
compliance:
  license_allow:
    - "MIT"
    - "Apache-2.0"
    - "GPL-3.0"  # Add new license
```

### Disable test file filtering
```yaml
# Edit configs/default.yaml
cleaning:
  drop_tests: false  # Keep test files
```

### Change output format
```yaml
# Edit configs/default.yaml
output:
  type: "rag"  # Change from "finetune"
```

## Environment Variables

```bash
# GitHub token (recommended for >20 repos)
export GITHUB_TOKEN=your_token_here

# Add to shell profile for persistence
echo 'export GITHUB_TOKEN=your_token_here' >> ~/.bashrc
```

## Troubleshooting

### Rate limit exceeded
```bash
# Set GitHub token
export GITHUB_TOKEN=ghp_...
```

### No repositories found
```yaml
# Use broader search query
sources:
  github:
    query: "language:Python stars:>10"
```

### Pipeline crashes
```bash
# Check logs
cat reports/provenance.jsonl | tail -100

# Run tiny config first
make run-tiny

# Clean and retry
make clean && make run
```

### Low example count
```yaml
# Reduce filters
cleaning:
  drop_tests: false
  max_file_mb: 2.0
```

## Pipeline Workflow

```
1. Discovery    → Fetch repos from GitHub
2. License      → Check license compliance
3. Security     → Scan for secrets/vulnerabilities
4. Cleaning     → Filter and deduplicate
5. Extraction   → Extract code examples
6. Transform    → Convert to schema
7. Finalize     → Split and package
```

## Output Schema

### Fine-Tuning Format (JSONL)
```json
{
  "id": "uuid",
  "task": "codegen",
  "input": "function signature + docstring",
  "output": "function body",
  "metadata": {
    "repo": "owner/name",
    "path": "file.py",
    "license": "MIT",
    "split": "train"
  }
}
```

### Metrics Format
```json
{
  "discovery": {"repos_cloned": 18},
  "compliance": {"files_scanned": 2500, "quarantined": 125},
  "extraction": {"examples_extracted": 5234},
  "quality": {"docstring_rate": 0.66}
}
```

## Directory Structure

```
code-curation/
├── pipeline/        # Core modules
├── configs/         # Configuration files
├── schemas/         # JSON schemas
├── tests/           # Test suite
├── data/
│   ├── raw/        # Downloaded repos
│   ├── quarantine/ # Rejected files
│   └── curated/    # Final outputs
├── reports/        # Logs and metrics
└── notebooks/      # Exploration
```

## Common Use Cases

### 1. Quick validation
```bash
make run-tiny
cat reports/metrics.json | python3 -m json.tool
```

### 2. Large-scale curation
```yaml
# Edit configs/production.yaml
sources:
  github:
    max_repos: 100
```
```bash
python3 -m pipeline.cli run --config configs/production.yaml
```

### 3. Custom task
```bash
# Copy and modify config
cp configs/default.yaml configs/my-task.yaml
# Edit my-task.yaml
python3 -m pipeline.cli run --config configs/my-task.yaml
```

### 4. Quality analysis
```bash
# Extract quality metrics
cat reports/metrics.json | python3 -c "import json, sys; m=json.load(sys.stdin); print('Docstring rate:', m['quality']['docstring_rate'])"
```

## Integration Examples

### Hugging Face Datasets
```python
from datasets import load_dataset

dataset = load_dataset('json', data_files={
    'train': 'data/curated/ft/v1/train.jsonl',
    'validation': 'data/curated/ft/v1/val.jsonl',
    'test': 'data/curated/ft/v1/test.jsonl'
})
```

### PyTorch DataLoader
```python
import json
from torch.utils.data import Dataset

class CodeDataset(Dataset):
    def __init__(self, jsonl_path):
        self.examples = []
        with open(jsonl_path) as f:
            for line in f:
                self.examples.append(json.loads(line))
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        return self.examples[idx]

train_dataset = CodeDataset('data/curated/ft/v1/train.jsonl')
```

## Documentation Links

- **Setup**: [GETTING_STARTED.md](GETTING_STARTED.md)
- **User Guide**: [PROJECT_README.md](PROJECT_README.md)
- **Technical Details**: [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md)
- **Implementation**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## Support

### Check Installation
```bash
python3 verify_installation.py
```

### Verify Reproducibility
```bash
# Run twice, compare hashes
make clean && make run
# Note hash from reports/metrics.json
make clean && make run
# Hashes should match
```

### Review Quality
```bash
# Manual inspection
head -n 10 data/curated/ft/v1/train.jsonl | python3 -m json.tool

# Statistical summary
cat reports/metrics.json | python3 -m json.tool | grep -A 5 quality
```

---

**Quick Start**: `make install` → `make run-tiny` → Check `reports/metrics.json`
