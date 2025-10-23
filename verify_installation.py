#!/usr/bin/env python3
"""
Verification script to check if the pipeline is properly installed.
Run this before using the pipeline to ensure everything is set up correctly.
"""

import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_directory_structure():
    """Check if all required directories exist."""
    required_dirs = [
        "pipeline",
        "configs",
        "schemas",
        "tests",
        "data/raw",
        "data/quarantine",
        "data/curated/ft",
        "data/curated/rag",
        "reports",
        "notebooks"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Missing directory: {dir_path}")
            all_exist = False
    
    return all_exist


def check_pipeline_modules():
    """Check if all pipeline modules are present."""
    required_modules = [
        "pipeline/__init__.py",
        "pipeline/cli.py",
        "pipeline/config.py",
        "pipeline/discover.py",
        "pipeline/license.py",
        "pipeline/security.py",
        "pipeline/clean.py",
        "pipeline/branch_codegen.py",
        "pipeline/transform.py",
        "pipeline/finalize.py",
        "pipeline/metrics.py",
        "pipeline/log.py",
    ]
    
    all_exist = True
    for module in required_modules:
        path = Path(module)
        if path.exists():
            print(f"✅ Module exists: {module}")
        else:
            print(f"❌ Missing module: {module}")
            all_exist = False
    
    return all_exist


def check_config_files():
    """Check if configuration files exist."""
    required_configs = [
        "configs/default.yaml",
        "configs/tiny.yaml",
        "schemas/common.schema.json",
        "schemas/codegen.schema.json",
    ]
    
    all_exist = True
    for config in required_configs:
        path = Path(config)
        if path.exists():
            print(f"✅ Config exists: {config}")
        else:
            print(f"❌ Missing config: {config}")
            all_exist = False
    
    return all_exist


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        ("yaml", "pyyaml"),
        ("requests", "requests"),
        ("pytest", "pytest"),
        ("jsonschema", "jsonschema"),
    ]
    
    all_installed = True
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"✅ Package installed: {package_name}")
        except ImportError:
            print(f"❌ Missing package: {package_name}")
            all_installed = False
    
    return all_installed


def check_documentation():
    """Check if documentation files exist."""
    docs = [
        "README.md",
        "PROJECT_README.md",
        "TECHNICAL_REPORT.md",
        "GETTING_STARTED.md",
        "IMPLEMENTATION_SUMMARY.md",
        "reports/README.md",
    ]
    
    all_exist = True
    for doc in docs:
        path = Path(doc)
        if path.exists():
            print(f"✅ Documentation exists: {doc}")
        else:
            print(f"❌ Missing documentation: {doc}")
            all_exist = False
    
    return all_exist


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("PIPELINE INSTALLATION VERIFICATION")
    print("=" * 70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Directory Structure", check_directory_structure),
        ("Pipeline Modules", check_pipeline_modules),
        ("Configuration Files", check_config_files),
        ("Dependencies", check_dependencies),
        ("Documentation", check_documentation),
    ]
    
    results = {}
    for check_name, check_func in checks:
        print(f"\n--- {check_name} ---")
        results[check_name] = check_func()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 All checks passed! The pipeline is ready to use.")
        print("\nNext steps:")
        print("  1. (Optional) Set GITHUB_TOKEN environment variable")
        print("  2. Run: make run-tiny")
        print("  3. Check outputs in data/curated/ and reports/")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Missing dependencies: run 'make install' or 'pip install -r requirements.txt'")
        print("  - Missing directories: they should be created automatically")
        print("  - Missing files: ensure you have the complete repository")
        return 1


if __name__ == "__main__":
    sys.exit(main())
