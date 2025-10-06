# 💡 Usage Examples

This document provides concrete examples of how to use the Secure Data Curation Pipeline.

## 🎬 Basic Usage

### Run with Default Settings
```bash
# Using make
make run

# Using python directly
python3 -m pipeline.cli run --config configs/default.yaml
```

### Clean Previous Runs
```bash
make clean
```

## 📁 Working with Your Data

### Example 1: Process Local Python Project
```bash
# 1. Copy your project to sample_code
cp -r ~/my-python-project data/sample_code/

# 2. Run pipeline
make run

# 3. Check outputs
ls -la data/curated/ft/v1/
ls -la data/curated/rag/v1/
```

### Example 2: Custom Configuration
```bash
# Create custom config
cat > configs/my_project.yaml << 'EOF'
discovery_mode: local
discovery_sources:
  - /home/user/projects/awesome-lib
  - /home/user/projects/util-functions
max_repos: 5

allowed_licenses:
  - MIT
  - Apache-2.0

security_checks:
  - bandit
  - secrets

task_branch: codegen

output_formats:
  - ft
  - rag

train_split: 0.7
val_split: 0.15
test_split: 0.15
EOF

# Run with custom config
python3 -m pipeline.cli run --config configs/my_project.yaml
```

### Example 3: Strict License Mode
```bash
# Edit config
cat > configs/strict.yaml << 'EOF'
discovery_mode: local
discovery_sources:
  - data/sample_code
license_strict: true  # Reject repos without explicit license
allowed_licenses:
  - MIT
EOF

# Run
python3 -m pipeline.cli run --config configs/strict.yaml
```

## 🔍 Inspecting Outputs

### View Fine-Tuning Data
```bash
# Pretty print one record
head -n 1 data/curated/ft/v1/train.jsonl | python3 -m json.tool

# Count records per split
wc -l data/curated/ft/v1/*.jsonl

# View all train records
cat data/curated/ft/v1/train.jsonl | while read line; do
    echo "$line" | python3 -m json.tool
    echo "---"
done | less
```

### View RAG Data
```bash
# Pretty print one record
head -n 1 data/curated/rag/v1/train.jsonl | python3 -m json.tool

# Extract just content fields
cat data/curated/rag/v1/train.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    record = json.loads(line)
    print(record['content'])
    print('='*70)
"
```

### Analyze Metrics
```bash
# View all metrics
cat reports/metrics.json | python3 -m json.tool

# Extract specific metrics
python3 << 'EOF'
import json
with open('reports/metrics.json') as f:
    metrics = json.load(f)
    
print("Pipeline Summary:")
print(f"  Repos discovered: {metrics['discovery']['total_repos_discovered']}")
print(f"  Files processed: {metrics['discovery']['total_files_discovered']}")
print(f"  Examples extracted: {metrics['extraction']['total_examples']}")
print(f"  Final records: {metrics['output']['total_records']}")
print(f"  Dedup ratio: {metrics['cleaning']['dedup_ratio_percent']}%")
EOF
```

### Explore Provenance Log
```bash
# View first 5 entries
head -n 5 reports/provenance.jsonl | python3 -m json.tool

# Count entries by stage
python3 << 'EOF'
import json
from collections import Counter

stages = []
with open('reports/provenance.jsonl') as f:
    for line in f:
        entry = json.loads(line)
        stages.append(entry['stage'])

counts = Counter(stages)
print("Entries by stage:")
for stage, count in sorted(counts.items()):
    print(f"  {stage}: {count}")
EOF

# Find all quarantined files
python3 << 'EOF'
import json

print("Quarantined files:")
with open('reports/provenance.jsonl') as f:
    for line in f:
        entry = json.loads(line)
        if entry['status'] == 'quarantined':
            print(f"  {entry['file_path']} - {entry['stage']}")
EOF
```

## 🧪 Testing Different Scenarios

### Scenario 1: Process Multiple Directories
```yaml
# configs/multi_source.yaml
discovery_mode: local
discovery_sources:
  - data/sample_code
  - /path/to/project1
  - /path/to/project2
  - /path/to/project3
max_repos: 10
```

### Scenario 2: High Security Settings
```yaml
# configs/high_security.yaml
security_checks:
  - bandit
  - secrets
  - malware
bandit_severity: high  # Only high severity issues

license_strict: true   # Must have explicit license

exclude_patterns:
  - "*/test/*"
  - "*/tests/*"
  - "*/vendor/*"
  - "*/__pycache__/*"
  - "*/examples/*"     # Also exclude examples
  - "*/docs/*"         # And docs
```

### Scenario 3: Minimal Cleaning
```yaml
# configs/minimal_cleaning.yaml
exclude_patterns:
  - "*/__pycache__/*"  # Only exclude pycache

min_file_size: 1       # Accept very small files
max_file_size: 10485760  # Accept up to 10MB

format_code: false     # Don't format
```

### Scenario 4: Custom Splits
```yaml
# configs/custom_splits.yaml
train_split: 0.9       # 90% training
val_split: 0.05        # 5% validation
test_split: 0.05       # 5% test

random_seed: 123       # Different seed
```

## 📊 Analysis Examples

### Count Functions Extracted
```bash
python3 << 'EOF'
import json

functions = set()
with open('data/curated/ft/v1/train.jsonl') as f:
    for line in f:
        record = json.loads(line)
        func_name = record['metadata'].get('function_name', 'unknown')
        functions.add(func_name)

print(f"Unique functions extracted: {len(functions)}")
for func in sorted(functions):
    print(f"  - {func}")
EOF
```

### Find Functions with Docstrings
```bash
python3 << 'EOF'
import json

with_docs = 0
without_docs = 0

for split in ['train', 'val', 'test']:
    with open(f'data/curated/ft/v1/{split}.jsonl') as f:
        for line in f:
            record = json.loads(line)
            if record['metadata'].get('has_docstring'):
                with_docs += 1
            else:
                without_docs += 1

total = with_docs + without_docs
print(f"Functions with docstrings: {with_docs}/{total} ({with_docs/total*100:.1f}%)")
print(f"Functions without docstrings: {without_docs}/{total} ({without_docs/total*100:.1f}%)")
EOF
```

### Calculate Average Code Length
```bash
python3 << 'EOF'
import json

lengths = []
for split in ['train', 'val', 'test']:
    with open(f'data/curated/ft/v1/{split}.jsonl') as f:
        for line in f:
            record = json.loads(line)
            code_length = len(record['output'])
            lengths.append(code_length)

if lengths:
    avg_length = sum(lengths) / len(lengths)
    min_length = min(lengths)
    max_length = max(lengths)
    
    print(f"Code output statistics:")
    print(f"  Average length: {avg_length:.0f} characters")
    print(f"  Min length: {min_length} characters")
    print(f"  Max length: {max_length} characters")
    print(f"  Total samples: {len(lengths)}")
EOF
```

## 🔄 Workflow Examples

### Workflow 1: Iterative Refinement
```bash
# 1. Initial run
make run

# 2. Check metrics
cat reports/metrics.json

# 3. Too many files excluded? Adjust patterns
nano configs/default.yaml  # Edit exclude_patterns

# 4. Clean and re-run
make clean
make run

# 5. Compare metrics
cat reports/metrics.json
```

### Workflow 2: Quality Control
```bash
# 1. Run pipeline
make run

# 2. Check quarantined files
ls -R data/quarantine/

# 3. Review provenance for quarantined files
grep quarantined reports/provenance.jsonl | python3 -m json.tool

# 4. Adjust security settings if needed
nano configs/default.yaml

# 5. Re-run
make clean && make run
```

### Workflow 3: Dataset Validation
```bash
# 1. Run pipeline
make run

# 2. Validate JSONL format
python3 << 'EOF'
import json

def validate_file(filepath):
    with open(filepath) as f:
        for i, line in enumerate(f, 1):
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error in {filepath} line {i}: {e}")
                return False
    return True

for split in ['train', 'val', 'test']:
    for format in ['ft', 'rag']:
        filepath = f'data/curated/{format}/v1/{split}.jsonl'
        if validate_file(filepath):
            print(f"✅ {filepath} is valid")
        else:
            print(f"❌ {filepath} has errors")
EOF

# 3. Validate schema compliance
python3 << 'EOF'
import json

with open('data/curated/ft/v1/train.jsonl') as f:
    for i, line in enumerate(f, 1):
        record = json.loads(line)
        required = ['instruction', 'input', 'output', 'metadata']
        missing = [field for field in required if field not in record]
        if missing:
            print(f"Record {i} missing fields: {missing}")
        else:
            print(f"✅ Record {i} valid")
EOF
```

## 🎯 Use Case Examples

### Use Case 1: Prepare Data for GPT Fine-Tuning
```bash
# 1. Configure for code generation
cat > configs/gpt_finetune.yaml << 'EOF'
discovery_mode: local
discovery_sources:
  - /path/to/quality/python/libs
task_branch: codegen
output_formats:
  - ft  # Only need fine-tuning format
train_split: 0.9
val_split: 0.1
test_split: 0.0  # No test split needed
EOF

# 2. Run pipeline
python3 -m pipeline.cli run --config configs/gpt_finetune.yaml

# 3. Convert to OpenAI format
python3 << 'EOF'
import json

# Convert to OpenAI's format
with open('data/curated/ft/v1/train.jsonl') as fin:
    with open('data/curated/ft/v1/train_openai.jsonl', 'w') as fout:
        for line in fin:
            record = json.loads(line)
            openai_record = {
                "messages": [
                    {"role": "system", "content": "You are a Python code completion assistant."},
                    {"role": "user", "content": record['input']},
                    {"role": "assistant", "content": record['output']}
                ]
            }
            fout.write(json.dumps(openai_record) + '\n')

print("✅ Converted to OpenAI format: data/curated/ft/v1/train_openai.jsonl")
EOF
```

### Use Case 2: Prepare Data for RAG System
```bash
# 1. Configure for RAG
cat > configs/rag_prep.yaml << 'EOF'
discovery_mode: local
discovery_sources:
  - /path/to/python/codebase
task_branch: codegen
output_formats:
  - rag  # Only need RAG format
EOF

# 2. Run pipeline
python3 -m pipeline.cli run --config configs/rag_prep.yaml

# 3. Prepare for vector database
python3 << 'EOF'
import json

# Extract content and metadata for vector DB
documents = []
with open('data/curated/rag/v1/train.jsonl') as f:
    for line in f:
        record = json.loads(line)
        documents.append({
            "id": record['id'],
            "text": record['content'],  # For embedding
            "metadata": record['metadata']
        })

with open('data/curated/rag/v1/for_embedding.json', 'w') as f:
    json.dump(documents, f, indent=2)

print(f"✅ Prepared {len(documents)} documents for embedding")
EOF
```

## 🚨 Troubleshooting Examples

### No Examples Extracted
```bash
# Check if files are being processed
cat reports/provenance.jsonl | grep -c "clean.*success"

# Check if files have functions
python3 << 'EOF'
import ast
from pathlib import Path

for py_file in Path('data/raw').rglob('*.py'):
    try:
        content = py_file.read_text()
        tree = ast.parse(content)
        funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        print(f"{py_file}: {len(funcs)} functions")
    except:
        print(f"{py_file}: ERROR")
EOF
```

### Files Getting Quarantined
```bash
# Check why files are quarantined
python3 << 'EOF'
import json

print("Quarantine reasons:")
with open('reports/provenance.jsonl') as f:
    for line in f:
        entry = json.loads(line)
        if entry['status'] == 'quarantined':
            print(f"\n{entry['file_path']}:")
            print(f"  Stage: {entry['stage']}")
            print(f"  Metadata: {entry['metadata']}")
EOF
```

## 📚 Advanced Examples

### Pipeline as Library
```python
# custom_script.py
from pathlib import Path
from pipeline.config import PipelineConfig
from pipeline.log import ProvenanceLogger
from pipeline.metrics import MetricsCollector
from pipeline.branch_codegen import CodeGenExtractor

# Load config
config = PipelineConfig.from_yaml('configs/default.yaml')

# Initialize logger
logger = ProvenanceLogger('custom_reports/provenance.jsonl')

# Extract examples
extractor = CodeGenExtractor(config, logger)
examples = extractor.extract_all(Path('data/raw'))

print(f"Extracted {len(examples)} examples")

# Process examples your way
for example in examples:
    print(f"Function: {example['function_name']}")
    print(f"Lines: {example['line_start']}-{example['line_end']}")
    print()
```

---

For more information, see:
- `README.md` - Full documentation
- `QUICKSTART.md` - Quick start guide
- `configs/default.yaml` - Configuration options
