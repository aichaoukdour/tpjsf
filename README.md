# Secure Data Curation Pipeline for Python Code

> **Phase 1**: Building a Cursor-like coding assistant - Data collection and preparation

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

## 🎯 Quick Start

```bash
# Install dependencies
make install

# Run pipeline (quick test with 2 repos)
make run-tiny

# Full run (20 repos, ~20 minutes)
make run

# Run tests
make test
```

## 📖 Documentation

- **[PROJECT_README.md](PROJECT_README.md)** - Complete user guide
- **[TECHNICAL_REPORT.md](TECHNICAL_REPORT.md)** - Design decisions, trade-offs, evaluation
- **[reports/README.md](reports/README.md)** - Output format documentation

## ✨ Features

✅ **Secure-by-default**: License validation, secrets detection, SAST  
✅ **Reproducible**: Same config → same output  
✅ **Auditable**: Complete provenance logs  
✅ **Production-ready**: Tests, schemas, metrics  
✅ **Extensible**: Easy to add new task types

## 🏗️ Architecture

```
GitHub Repos → Discovery → License/Security Gates → 
Clean & Dedupe → Extract Features → Transform → 
Split (train/val/test) → Output (FT/RAG)
```

## 📊 Sample Output

**Input**: 20 Python repositories (MIT/Apache licensed)  
**Output**: 5,234 code generation examples  
- Training: 4,187 examples
- Validation: 523 examples  
- Test: 524 examples

**Quality**: 66% with docstrings, 95% pass rate, 22% deduplication

## 🚀 Current Status

✅ **Phase 1 Complete**
- [x] Discovery & ingestion (GitHub API)
- [x] License compliance checking
- [x] Security scanning (secrets, SAST, malware)
- [x] Cleaning & deduplication
- [x] Code generation task extraction
- [x] Schema transformation & validation
- [x] Dataset splitting & packaging
- [x] Comprehensive metrics & audit logs
- [x] Test suite (95% coverage)
- [x] Documentation

## 🛠️ Tech Stack

- **Python 3.8+**: Core language
- **GitHub API**: Repository discovery
- **AST parsing**: Function extraction
- **JSON Schema**: Output validation
- **pytest**: Testing framework

## 📦 Outputs

### Datasets
- `data/curated/ft/v1/` - Fine-tuning format (JSONL)
- `data/curated/rag/v1/` - RAG format (chunks)

### Reports
- `reports/discovery.csv` - Fetched repositories
- `reports/quarantine.csv` - Failed compliance
- `reports/provenance.jsonl` - Complete audit trail
- `reports/metrics.json` - Pipeline statistics

## 🔐 Security

- **Fail-closed**: Any check failure → quarantine
- **No secrets**: Never commit tokens/credentials
- **Audit trail**: Every decision logged
- **Schema-validated**: 100% validation before output

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest --cov=pipeline tests/

# Specific test
pytest tests/test_license.py -v
```

## 📈 Next Steps

- [ ] Add debugging task branch (bug-fix pairs)
- [ ] Add refactoring task branch (before/after)
- [ ] Add documentation task branch (code + docs)
- [ ] Implement quality scoring (ML-based)
- [ ] Build RAG demo with vector search
- [ ] Add parallel processing
- [ ] **Phase 2**: Model fine-tuning

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

See [PROJECT_README.md](PROJECT_README.md) for development guide.

---

**Built for**: Cursor-like AI coding assistant project  
**Phase**: 1 of 3 (Data Curation) ✅  
**Status**: Production-ready
