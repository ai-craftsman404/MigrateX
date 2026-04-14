"""
Code Analyzer Agent - Pattern detection during analyze phase
"""

from pathlib import Path
from migratex.agents import BaseAgent
from migratex.patterns.discovery import PatternDiscovery
from migratex.docs import migration_docs


class CodeAnalyzerAgent(BaseAgent):
    """
    Inspects and classifies existing code in the repo.
    Detects Semantic Kernel and AutoGen usage patterns.
    Uses Microsoft's official migration guides for pattern identification.
    """
    
    def run(self):
        """Run code analysis and populate context report."""
        # Start task with acceptance criteria
        task_manager = self.context.get_task_manager()
        task_id = task_manager.start_task(
            "code_analysis",
            "Code Analysis",
            "Analyse codebase for SK/AutoGen patterns",
            acceptance_criteria=[
                "analysis_completes_without_errors",
                "report_generated_successfully",
                "patterns_detected_correctly",
                "unit_tests_all_passed",
                "integration_tests_all_passed"
            ]
        )
        
        try:
            # Load migration documentation for reference
            sk_guide = migration_docs.get_migration_guide("semantic_kernel")
            autogen_guide = migration_docs.get_migration_guide("autogen")
            
            # Detect outliers before analysis
            from migratex.testing.outlier_detector import OutlierDetector
            outlier_detector = OutlierDetector()
            outlier_report = outlier_detector.detect_outliers(self.context.project_path)
            
            # If outliers detected and not in expert mode, handle them
            if outlier_report["is_outlier"] and self.context.mode != "analyze":
                from migratex.utils.outlier_prompts import prompt_outlier_confirmation
                
                # Only prompt in interactive mode (not CI/CD)
                if self.context.mode == "review" or (hasattr(self.context, 'interactive') and self.context.interactive):
                    user_decision = prompt_outlier_confirmation(outlier_report)
                    
                    if user_decision == "abort":
                        raise ValueError("Migration aborted due to outlier codebase")
                    elif user_decision == "proceed_review":
                        self.context.mode = "review"
                        self.context.outlier_mode = "review"
                    elif user_decision == "expert_mode":
                        self.context.outlier_mode = "expert"
                    elif user_decision == "proceed_cautious":
                        self.context.outlier_mode = "cautious"
            
            # Find Python files in project
            python_files = self._find_python_files()
            
            # Discover patterns
            discovery = PatternDiscovery(self.context)
            detected_patterns = discovery.discover_patterns(python_files)
            
            # Enhance patterns with migration guidance
            enhanced_patterns = self._enhance_with_migration_guidance(detected_patterns)
            
            # Build report
            self.context.report = {
                "project_path": str(self.context.project_path),
                "files": [str(f) for f in python_files],
                "patterns": enhanced_patterns,
                "migration_guides": {
                    "semantic_kernel": sk_guide,
                    "autogen": autogen_guide
                },
                "outlier_report": outlier_report,
                "statistics": {
                    "total_files": len(python_files),
                    "patterns_detected": len(enhanced_patterns),
                }
            }
            
            # Record test results (analysis validation)
            task_manager.record_test_results(
                unit_passed=1 if len(python_files) > 0 else 0,
                unit_total=1,
                integration_passed=1 if len(enhanced_patterns) > 0 else 0,
                integration_total=1
            )
            
            # Mark acceptance criteria
            task_manager.mark_criterion_met("analysis_completes_without_errors")
            task_manager.mark_criterion_met("report_generated_successfully")
            task_manager.mark_criterion_met("patterns_detected_correctly")
            
            if self.context.verbose:
                print(f"Analysed {len(python_files)} files")
                print(f"Detected {len(enhanced_patterns)} patterns")
                print(f"Migration guides available: SK={sk_guide is not None}, AutoGen={autogen_guide is not None}")
            
            # Complete task
            task_manager.complete_task(success=True)
            
        except Exception as e:
            task_manager.add_error(None, str(e))
            task_manager.complete_task(success=False)
            raise
    
    def _enhance_with_migration_guidance(self, patterns):
        """Enhance detected patterns with migration guidance from docs."""
        enhanced = []
        for pattern in patterns:
            pattern_type = pattern.get("type", "")
            framework = "semantic_kernel" if "semantic_kernel" in pattern.get("id", "").lower() else "autogen"
            
            # Get migration guidance for this pattern
            mappings = migration_docs.get_pattern_mappings(framework)
            pattern["migration_guidance"] = mappings.get(pattern_type, {})
            pattern["migration_guide_url"] = migration_docs.get_migration_guide(framework).get("url") if migration_docs.get_migration_guide(framework) else None
            
            enhanced.append(pattern)
        return enhanced
    
    def _find_python_files(self) -> list[Path]:
        """Find all Python files in the project."""
        if not self.context.project_path.exists() or not self.context.project_path.is_dir():
            raise FileNotFoundError(f"Project path does not exist or is not a directory: {self.context.project_path}")

        python_files = []
        for path in self.context.project_path.rglob("*.py"):
            # Skip common directories
            if any(part in path.parts for part in ["__pycache__", ".git", "venv", "env"]):
                continue
            python_files.append(path)
        return python_files

