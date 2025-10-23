"""Command-line interface for the pipeline."""

import sys
import argparse
from pathlib import Path
import shutil

from .config import PipelineConfig
from .discover import RepositoryDiscovery
from .license import LicenseChecker
from .security import SecurityScanner
from .clean import DataCleaner
from .branch_codegen import CodeGenExtractor
from .transform import SchemaTransformer
from .finalize import DatasetFinalizer
from .metrics import MetricsCollector
from .log import ProvenanceLogger, QuarantineLogger, DiscoveryLogger


class Pipeline:
    """Main pipeline orchestrator."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.metrics = MetricsCollector()
        
        # Initialize loggers
        reports_dir = config.reports_dir
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.provenance_logger = ProvenanceLogger(reports_dir / "provenance.jsonl")
        self.quarantine_logger = QuarantineLogger(reports_dir / "quarantine.csv")
        self.discovery_logger = DiscoveryLogger(reports_dir / "discovery.csv")
    
    def run(self):
        """Run the complete pipeline."""
        print(f"Starting pipeline run: {self.config.run_id}")
        
        # Set run info
        self.metrics.set_run_info(self.config.run_id, self.config.to_dict())
        
        # Step 1: Discovery
        print("\n[Step 1] Discovery & Fetching")
        successful = self._run_discovery()
        
        # Step 2: License & Security
        print("\n[Step 2] License & Security Gating")
        license_passed, security_passed, quarantined = self._run_compliance()
        
        # Step 3: Cleaning & Deduplication
        print("\n[Step 3] Cleaning & Deduplication")
        files_before, files_after, dedup_ratio = self._run_cleaning()
        
        # Step 4: Task-specific extraction
        print(f"\n[Step 4] Task Extraction ({self.config.branch})")
        examples = self._run_extraction()
        
        # Step 5: Transformation
        print("\n[Step 5] Schema Transformation")
        records = self._run_transformation(examples)
        
        # Step 6: Output formatting
        print(f"\n[Step 6] Output Formatting ({self.config.output.type})")
        output_info = self._run_output(records)
        
        # Step 7: Finalization
        print("\n[Step 7] Finalization & Metrics")
        self._finalize(output_info, records)
        
        print("\n✓ Pipeline completed successfully!")
        self.metrics.print_summary()
    
    def _run_discovery(self) -> int:
        """Run discovery step."""
        discovery = RepositoryDiscovery(self.config, self.discovery_logger)
        successful = discovery.discover_and_fetch()
        
        self.metrics.set_discovery_metrics(
            num_repos=self.config.sources.github.max_repos,
            successful=successful
        )
        
        return successful
    
    def _run_compliance(self):
        """Run compliance checking."""
        license_checker = LicenseChecker(set(self.config.compliance.license_allow))
        security_scanner = SecurityScanner(
            enable_sast=self.config.security.enable_sast,
            enable_secrets=self.config.security.enable_secrets,
            enable_malware=self.config.security.enable_malware
        )
        
        raw_dir = self.config.data_dir / "raw"
        quarantine_dir = self.config.data_dir / "quarantine"
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        
        files_scanned = 0
        license_passed_count = 0
        security_passed_count = 0
        quarantined_count = 0
        
        # Process each repository
        for repo_dir in raw_dir.iterdir():
            if not repo_dir.is_dir():
                continue
            
            repo_name = repo_dir.name
            
            # Check license
            is_allowed, detected_license, reason = license_checker.check_repo(repo_dir)
            
            if not is_allowed:
                # Quarantine entire repo
                self.quarantine_logger.log(
                    repo=repo_name,
                    path=str(repo_dir),
                    reason=reason,
                    checker="license",
                    evidence=detected_license or "None"
                )
                quarantined_count += 1
                
                # Move to quarantine
                dest = quarantine_dir / repo_name
                if not dest.exists():
                    shutil.move(str(repo_dir), str(dest))
                
                continue
            
            license_passed_count += 1
            
            # Check files for security
            for py_file in repo_dir.rglob("*.py"):
                files_scanned += 1
                
                is_safe, findings = security_scanner.scan_file(py_file)
                
                if not is_safe:
                    # Quarantine file
                    self.quarantine_logger.log(
                        repo=repo_name,
                        path=str(py_file.relative_to(repo_dir)),
                        reason=f"Security: {len(findings)} issue(s)",
                        checker="security",
                        evidence=str(findings[:3])  # First 3 findings
                    )
                    quarantined_count += 1
                    
                    # Remove file
                    py_file.unlink()
                else:
                    security_passed_count += 1
                    
                    # Log provenance
                    file_hash = security_scanner.compute_file_hash(py_file)
                    self.provenance_logger.log({
                        "repo": repo_name,
                        "path": str(py_file.relative_to(repo_dir)),
                        "sha": "",  # Would need git info
                        "hash": file_hash,
                        "status": "kept",
                        "reason": "passed all checks",
                        "license": detected_license or "Unknown",
                    })
        
        self.quarantine_logger.flush()
        
        self.metrics.set_compliance_metrics(
            files_scanned=files_scanned,
            license_passed=license_passed_count,
            security_passed=security_passed_count,
            quarantined=quarantined_count
        )
        
        return license_passed_count, security_passed_count, quarantined_count
    
    def _run_cleaning(self):
        """Run cleaning and deduplication."""
        cleaner = DataCleaner(
            drop_tests=self.config.cleaning.drop_tests,
            max_file_mb=self.config.cleaning.max_file_mb,
            dedupe_level=self.config.cleaning.dedupe_level
        )
        
        raw_dir = self.config.data_dir / "raw"
        files_before = 0
        files_after = 0
        
        for repo_dir in raw_dir.iterdir():
            if not repo_dir.is_dir():
                continue
            
            for py_file in list(repo_dir.rglob("*.py")):
                files_before += 1
                
                # Check if should skip
                should_skip, reason = cleaner.should_skip_file(py_file)
                
                if should_skip:
                    self.provenance_logger.log({
                        "repo": repo_dir.name,
                        "path": str(py_file.relative_to(repo_dir)),
                        "status": "dropped",
                        "reason": reason,
                    })
                    py_file.unlink()
                    continue
                
                # Clean content
                try:
                    with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    cleaned = cleaner.clean_content(content)
                    content_hash = cleaner.compute_hash(cleaned)
                    
                    # Check for duplicates
                    if cleaner.is_duplicate(content_hash):
                        self.provenance_logger.log({
                            "repo": repo_dir.name,
                            "path": str(py_file.relative_to(repo_dir)),
                            "hash": content_hash,
                            "status": "dropped",
                            "reason": "duplicate",
                        })
                        py_file.unlink()
                    else:
                        # Write cleaned content
                        with open(py_file, "w", encoding="utf-8") as f:
                            f.write(cleaned)
                        
                        files_after += 1
                
                except Exception as e:
                    self.provenance_logger.log({
                        "repo": repo_dir.name,
                        "path": str(py_file.relative_to(repo_dir)),
                        "status": "dropped",
                        "reason": f"error: {e}",
                    })
                    py_file.unlink()
        
        dedup_ratio = cleaner.get_dedup_ratio()
        
        self.metrics.set_cleaning_metrics(
            files_before=files_before,
            files_after=files_after,
            dedup_ratio=dedup_ratio
        )
        
        return files_before, files_after, dedup_ratio
    
    def _run_extraction(self):
        """Run task-specific extraction."""
        if self.config.branch != "codegen":
            raise NotImplementedError(f"Branch '{self.config.branch}' not implemented yet")
        
        extractor = CodeGenExtractor()
        raw_dir = self.config.data_dir / "raw"
        
        for repo_dir in raw_dir.iterdir():
            if not repo_dir.is_dir():
                continue
            
            repo_name = repo_dir.name
            
            for py_file in repo_dir.rglob("*.py"):
                try:
                    with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    extractor.extract_from_file(
                        file_path=py_file,
                        content=content,
                        repo_name=repo_name,
                        commit_sha="",  # Would need git info
                        license="Unknown"  # Would get from license check
                    )
                
                except Exception as e:
                    print(f"Error extracting from {py_file}: {e}")
        
        stats = extractor.get_statistics()
        
        self.metrics.set_extraction_metrics(
            task=self.config.branch,
            examples_extracted=stats["total_examples"],
            avg_length=stats["avg_function_length"],
            task_specific=stats
        )
        
        return extractor.examples
    
    def _run_transformation(self, examples):
        """Transform examples to common schema."""
        transformer = SchemaTransformer(self.config.branch)
        
        for example in examples:
            if self.config.branch == "codegen":
                transformer.transform_codegen(example)
        
        # Validate all records
        records = transformer.get_records()
        valid_count = sum(1 for r in transformer.validate_record(r) for r in records)
        
        print(f"Validated {valid_count}/{len(records)} records")
        
        return records
    
    def _run_output(self, records):
        """Format and save output."""
        finalizer = DatasetFinalizer(
            train_split=self.config.output.train_split,
            val_split=self.config.output.val_split,
            test_split=self.config.output.test_split
        )
        
        curated_dir = self.config.data_dir / "curated"
        
        if self.config.output.type == "finetune":
            output_info = finalizer.save_finetune_format(
                records, curated_dir, self.config.output.version
            )
        elif self.config.output.type == "rag":
            output_info = finalizer.save_rag_format(
                records, curated_dir, self.config.output.version
            )
        else:
            raise ValueError(f"Unknown output type: {self.config.output.type}")
        
        self.metrics.set_output_metrics(
            output_type=self.config.output.type,
            splits=output_info
        )
        
        return output_info
    
    def _finalize(self, output_info, records):
        """Finalize pipeline with metrics."""
        # Compute quality metrics
        quality = self.metrics.compute_quality_checks(records)
        self.metrics.set_quality_metrics(quality)
        
        # Flush loggers
        self.provenance_logger.flush()
        
        # Save metrics report
        self.metrics.save_report(self.config.reports_dir / "metrics.json")
        
        print(f"\nOutput saved to: {output_info.get('output_dir', 'N/A')}")
        print(f"Reports saved to: {self.config.reports_dir}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Secure Python Code Curation Pipeline")
    parser.add_argument("command", choices=["run"], help="Command to execute")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to config file")
    
    args = parser.parse_args()
    
    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    
    config = PipelineConfig.from_yaml(str(config_path))
    
    # Run pipeline
    if args.command == "run":
        pipeline = Pipeline(config)
        try:
            pipeline.run()
        except Exception as e:
            print(f"\n✗ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
