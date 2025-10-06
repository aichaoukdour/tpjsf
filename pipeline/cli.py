"""
CLI orchestrator for the data curation pipeline.
Main entry point for running the complete pipeline.
"""

import argparse
import sys
from pathlib import Path

from pipeline.config import PipelineConfig
from pipeline.log import ProvenanceLogger
from pipeline.metrics import MetricsCollector
from pipeline.discover import RepositoryDiscoverer
from pipeline.license import LicenseScanner
from pipeline.security import SecurityScanner
from pipeline.clean import CodeCleaner
from pipeline.branch_codegen import CodeGenExtractor
from pipeline.transform import SchemaTransformer
from pipeline.finalize import OutputFinalizer


class PipelineOrchestrator:
    """Orchestrates the entire data curation pipeline."""
    
    def __init__(self, config_path: str):
        """
        Initialize the orchestrator.
        
        Args:
            config_path: Path to configuration YAML file
        """
        print("="*70)
        print("🚀 SECURE DATA CURATION PIPELINE")
        print("="*70)
        
        # Load configuration
        self.config = PipelineConfig.from_yaml(config_path)
        self.config.validate()
        
        # Initialize directories
        self.data_dir = Path(self.config.data_dir)
        self.reports_dir = Path(self.config.reports_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Initialize logger and metrics
        self.logger = ProvenanceLogger(self.reports_dir / "provenance.jsonl")
        self.metrics = MetricsCollector()
        
        print(f"📋 Configuration loaded from {config_path}")
        print(f"📁 Data directory: {self.data_dir}")
        print(f"📊 Reports directory: {self.reports_dir}")
        print(f"🎯 Task branch: {self.config.task_branch}")
        print()
    
    def run(self):
        """Execute the complete pipeline."""
        try:
            # Step 1: Discovery
            print("\n" + "─"*70)
            print("STEP 1: DISCOVERY")
            print("─"*70)
            discoverer = RepositoryDiscoverer(self.config, self.logger)
            repos = discoverer.discover()
            discoverer.save_report(repos, self.reports_dir / "discovery.csv")
            self.metrics.compute_discovery_metrics(self.reports_dir / "discovery.csv")
            
            raw_dir = self.data_dir / "raw"
            
            # Step 2: License Scanning
            print("\n" + "─"*70)
            print("STEP 2: LICENSE VALIDATION")
            print("─"*70)
            license_scanner = LicenseScanner(self.config, self.logger)
            license_results = license_scanner.scan_all(raw_dir)
            self.metrics.add_metric("license", "compliant_repos", len(license_results["compliant"]))
            self.metrics.add_metric("license", "quarantined_repos", len(license_results["quarantined"]))
            
            # Step 3: Security Scanning
            print("\n" + "─"*70)
            print("STEP 3: SECURITY SCANNING")
            print("─"*70)
            security_scanner = SecurityScanner(self.config, self.logger)
            security_results = security_scanner.scan_all(raw_dir)
            self.metrics.compute_security_metrics(self.data_dir / "quarantine" / "security")
            
            # Step 4: Cleaning & Deduplication
            print("\n" + "─"*70)
            print("STEP 4: CLEANING & DEDUPLICATION")
            print("─"*70)
            cleaner = CodeCleaner(self.config, self.logger)
            clean_results = cleaner.clean_all(raw_dir)
            self.metrics.compute_deduplication_metrics(
                files_before=clean_results["total_files"],
                files_after=len(clean_results["cleaned_files"])
            )
            
            # Step 5: Task Branch Extraction
            print("\n" + "─"*70)
            print(f"STEP 5: TASK BRANCH - {self.config.task_branch.upper()}")
            print("─"*70)
            
            if self.config.task_branch == "codegen":
                extractor = CodeGenExtractor(self.config, self.logger)
                examples = extractor.extract_all(raw_dir)
            else:
                print(f"⚠️  Task branch '{self.config.task_branch}' is not fully implemented")
                print("    Using placeholder implementation")
                examples = []
            
            self.metrics.add_metric("extraction", "total_examples", len(examples))
            
            if not examples:
                print("\n⚠️  No examples extracted. Pipeline completed early.")
                self._finalize_pipeline(success=True, early_exit=True)
                return
            
            # Step 6: Schema Transformation
            print("\n" + "─"*70)
            print("STEP 6: SCHEMA TRANSFORMATION")
            print("─"*70)
            transformer = SchemaTransformer(self.config, self.logger)
            transformed = transformer.transform_all(examples)
            self.metrics.add_metric("transform", "transformed_records", len(transformed))
            
            # Step 7: Finalization & Output
            print("\n" + "─"*70)
            print("STEP 7: FINALIZATION & OUTPUT")
            print("─"*70)
            finalizer = OutputFinalizer(self.config, self.logger)
            finalize_results = finalizer.finalize_all(transformed)
            self.metrics.compute_output_metrics(self.data_dir / "curated")
            
            # Complete pipeline
            self._finalize_pipeline(success=True)
            
        except Exception as e:
            print(f"\n❌ Pipeline failed with error: {e}")
            import traceback
            traceback.print_exc()
            self._finalize_pipeline(success=False)
            sys.exit(1)
    
    def _finalize_pipeline(self, success: bool, early_exit: bool = False):
        """
        Finalize the pipeline run.
        
        Args:
            success: Whether pipeline completed successfully
            early_exit: Whether pipeline exited early (but successfully)
        """
        print("\n" + "="*70)
        print("📊 PIPELINE SUMMARY")
        print("="*70)
        
        # Save metrics
        self.metrics.save_metrics(self.reports_dir / "metrics.json")
        self.metrics.print_summary()
        
        # Print provenance stats
        prov_stats = self.logger.get_stats()
        print("📝 PROVENANCE LOG STATISTICS:")
        print(f"  • Total log entries: {prov_stats['total_entries']}")
        print(f"  • Unique files processed: {prov_stats['unique_files']}")
        print()
        
        if success:
            if early_exit:
                print("⚠️  Pipeline completed early (no data to process)")
            else:
                print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        else:
            print("❌ PIPELINE FAILED")
        
        print("="*70)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Secure Data Curation Pipeline for Python Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m pipeline.cli run --config configs/default.yaml
  python -m pipeline.cli run --config configs/custom.yaml
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the complete pipeline')
    run_parser.add_argument(
        '--config',
        type=str,
        default='configs/default.yaml',
        help='Path to configuration YAML file (default: configs/default.yaml)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'run':
        orchestrator = PipelineOrchestrator(args.config)
        orchestrator.run()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
