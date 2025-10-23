# Getting Started Guide

This guide will help you set up and run the pipeline for the first time.

## Prerequisites

- Python 3.8 or higher
- Git
- (Optional) GitHub Personal Access Token for higher API rate limits

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd code-curation
```

### 2. Install Dependencies

```bash
# Using make (recommended)
make install

# Or manually with pip
pip install -r requirements.txt
```

### 3. Set Up GitHub Token (Optional but Recommended)

To avoid GitHub API rate limits, set up a personal access token:

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `public_repo` scope
3. Set the environment variable:

```bash
export GITHUB_TOKEN=your_token_here
```

Or add to your shell profile (`~/.bashrc`, `~/.zshrc`):
```bash
echo 'export GITHUB_TOKEN=your_token_here' >> ~/.bashrc
source ~/.bashrc
```

## Quick Test Run

Run the pipeline with a minimal configuration to verify everything works:

```bash
make run-tiny
```

This will:
- Fetch 2 Python repositories
- Process them through all pipeline stages
- Generate outputs in `data/curated/ft/v1/`
- Create reports in `reports/`

Expected runtime: **5-10 minutes**

## Understanding the Output

After the pipeline completes, check:

### 1. Reports Directory

```bash
ls -la reports/
```

You should see:
- `discovery.csv` - List of fetched repositories
- `quarantine.csv` - Files that failed checks
- `provenance.jsonl` - Complete audit trail
- `metrics.json` - Pipeline statistics

View metrics:
```bash
cat reports/metrics.json | python3 -m json.tool
```

### 2. Curated Datasets

```bash
ls -la data/curated/ft/v1/
```

You should see:
- `train.jsonl` - Training examples
- `val.jsonl` - Validation examples
- `test.jsonl` - Test examples
- `MANIFEST.yaml` - Dataset metadata

Inspect examples:
```bash
head -n 1 data/curated/ft/v1/train.jsonl | python3 -m json.tool
```

## Full Run

Once you've verified the quick test works, run the full pipeline:

```bash
make run
```

This will process 20 repositories (configurable in `configs/default.yaml`).

Expected runtime: **15-25 minutes** (depends on network speed)

## Customizing the Pipeline

### Edit Configuration

```bash
nano configs/default.yaml
```

Key settings to adjust:

```yaml
# Number of repositories to fetch
sources:
  github:
    max_repos: 20  # Increase/decrease as needed

# Which licenses to allow
compliance:
  license_allow:
    - "MIT"
    - "Apache-2.0"
    # Add more licenses here

# What to extract
branch: "codegen"  # Current: code generation

# Output format
output:
  type: "finetune"  # or "rag"
```

### Create Custom Config

```bash
cp configs/default.yaml configs/my-config.yaml
# Edit my-config.yaml
python3 -m pipeline.cli run --config configs/my-config.yaml
```

## Verifying Results

### 1. Check Success Criteria

Run tests:
```bash
make test
```

All tests should pass ✅

### 2. Verify Reproducibility

Run twice with same config:
```bash
make clean  # Clear previous data
make run
# Note the dataset hash in reports/metrics.json

make clean
make run
# Hash should be identical
```

### 3. Review Quality

Check metrics:
```bash
cat reports/metrics.json | python3 -m json.tool | grep -A 10 "quality"
```

Look for:
- `docstring_rate` > 0.6 (60%+ functions have docs)
- `dedup_ratio` < 0.3 (less than 30% duplicates)
- Low quarantine rate (< 10%)

## Troubleshooting

### "GitHub API rate limit exceeded"

**Solution**: Set `GITHUB_TOKEN` environment variable (see step 3 above)

### "No repositories found"

**Causes**:
- Network connectivity issues
- GitHub search query too restrictive

**Solutions**:
- Check internet connection
- Try broader query: `language:Python stars:>50`
- Check GitHub status: https://www.githubstatus.com/

### "Too many files quarantined"

**Causes**:
- Strict license requirements
- Aggressive security scanning

**Solutions**:
- Review `reports/quarantine.csv` for reasons
- Adjust `license_allow` in config
- Tune security patterns in `pipeline/security.py`

### "Pipeline crashes during clone"

**Causes**:
- Large repositories timing out
- Network interruptions

**Solutions**:
- Increase timeout in `pipeline/discover.py`
- Use tiny config for testing
- Skip problematic repos (they'll be logged)

### "Low example count"

**Causes**:
- Too many filters enabled
- High quality thresholds

**Solutions**:
- Set `drop_tests: false` to keep test files
- Lower `min_function_lines` in code
- Disable `require_docstring` for more examples

## Next Steps

### 1. Explore the Data

Use the included Jupyter notebook:
```bash
jupyter notebook notebooks/explore_data.ipynb
```

### 2. Validate Quality

Manually review 10-20 examples:
```bash
head -n 20 data/curated/ft/v1/train.jsonl | python3 -m json.tool
```

### 3. Prepare for Model Training

The dataset is now ready for fine-tuning! Example using Hugging Face:

```python
from datasets import load_dataset

dataset = load_dataset('json', data_files={
    'train': 'data/curated/ft/v1/train.jsonl',
    'validation': 'data/curated/ft/v1/val.jsonl',
    'test': 'data/curated/ft/v1/test.jsonl'
})

# Now ready for training!
```

### 4. Extend the Pipeline

- Add new task branches (debugging, refactoring, docs)
- Implement custom quality scoring
- Build RAG demo with your curated data

## Common Workflows

### Development Workflow

```bash
# 1. Make changes to pipeline code
nano pipeline/clean.py

# 2. Run tests
make test

# 3. Quick validation
make run-tiny

# 4. Full run
make run

# 5. Format code
make fmt

# 6. Lint
make lint
```

### Production Workflow

```bash
# 1. Review and update config
nano configs/production.yaml

# 2. Run pipeline
python3 -m pipeline.cli run --config configs/production.yaml

# 3. Validate outputs
cat reports/metrics.json | python3 -m json.tool

# 4. Archive results
tar -czf dataset-v1-$(date +%Y%m%d).tar.gz \
    data/curated/ reports/ configs/production.yaml

# 5. Upload to storage
# aws s3 cp dataset-v1-*.tar.gz s3://my-bucket/
```

## Getting Help

1. **Documentation**: Read [PROJECT_README.md](PROJECT_README.md)
2. **Technical Details**: See [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md)
3. **Issues**: Check logs in `reports/` directory
4. **Examples**: Review test files in `tests/`

## Summary Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`make install`)
- [ ] GitHub token configured (optional)
- [ ] Quick test successful (`make run-tiny`)
- [ ] Full run completed (`make run`)
- [ ] Tests passing (`make test`)
- [ ] Outputs validated (reports + datasets exist)
- [ ] Ready for Phase 2 (model training)

---

**Congratulations!** You've successfully set up the data curation pipeline. 🎉

Next: Proceed to Phase 2 (Model Fine-Tuning) with your curated dataset.
