#!/bin/bash
# Demo script to showcase the pipeline

echo "=========================================="
echo "Secure Data Curation Pipeline - Demo"
echo "=========================================="
echo ""

# Check if pyyaml is installed
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install pyyaml
    echo ""
fi

# Clean previous runs
echo "Cleaning previous runs..."
make clean
echo ""

# Run the pipeline
echo "Running pipeline..."
echo ""
python3 -m pipeline.cli run --config configs/default.yaml
echo ""

# Show outputs
echo ""
echo "=========================================="
echo "📊 OUTPUTS GENERATED"
echo "=========================================="
echo ""

echo "Fine-tuning data:"
ls -lh data/curated/ft/v1/
echo ""

echo "RAG data:"
ls -lh data/curated/rag/v1/
echo ""

echo "Reports:"
ls -lh reports/
echo ""

echo "=========================================="
echo "📄 SAMPLE OUTPUT"
echo "=========================================="
echo ""
echo "Sample fine-tuning record:"
head -n 1 data/curated/ft/v1/train.jsonl | python3 -m json.tool
echo ""

echo "=========================================="
echo "✅ Demo complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Check outputs: data/curated/"
echo "  2. View metrics: cat reports/metrics.json | python3 -m json.tool"
echo "  3. Read docs: cat README.md"
echo "  4. Add your data to data/sample_code/ and run again!"
echo ""
