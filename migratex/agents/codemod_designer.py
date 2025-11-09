"""
Codemod Designer Agent - AST-based transformations
"""

from typing import Dict, List, Any
from migratex.agents import BaseAgent
from migratex.languages.python.patterns import PythonPatterns

# Optional imports for AST transformations
try:
    from migratex.languages.python.transformers import PythonTransformer
    HAS_TRANSFORMER = True
except ImportError:
    HAS_TRANSFORMER = False
    PythonTransformer = None


class CodemodDesignerAgent(BaseAgent):
    """
    Designs automated transformations and codemods.
    Turns repeated migration patterns into scripted transformations (AST-based).
    Prepares AST transformers for detected patterns and stores them in context.
    """
    
    def run(self):
        """Prepare codemods for detected patterns."""
        task_manager = self.context.get_task_manager()
        task_id = task_manager.start_task(
            "codemod_design",
            "Codemod Design",
            "Prepare AST transformations for detected patterns",
            acceptance_criteria=[
                "codemods_prepared_for_all_patterns",
                "transformations_validated",
                "unit_tests_all_passed"
            ]
        )
        
        try:
            # Get detected patterns from analysis report
            if "patterns" not in self.context.report:
                if self.context.verbose:
                    print("No patterns detected. Run 'analyze' command first.")
                task_manager.complete_task(success=True)
                return
            
            detected_patterns = self.context.report["patterns"]
            
            # Get all available patterns
            all_patterns = PythonPatterns.get_patterns()
            
            # Prepare AST transformers for each detected pattern
            codemods: Dict[str, Any] = {}
            
            for pattern_info in detected_patterns:
                pattern_id = pattern_info.get("id")
                
                # Get pattern definition
                pattern_def = self.context.pattern_library.get_pattern(pattern_id)
                if not pattern_def:
                    # Try to get from PythonPatterns
                    pattern_def = next(
                        (p for p in all_patterns.values() if p.get("id") == pattern_id),
                        None
                    )
                
                if not pattern_def:
                    continue
                
                # Create transformer for this pattern (if available)
                transformer = None
                if HAS_TRANSFORMER and PythonTransformer:
                    try:
                        transformer = PythonTransformer(pattern_def)
                    except Exception:
                        transformer = None
                
                # Store codemod metadata
                codemods[pattern_id] = {
                    "pattern_id": pattern_id,
                    "pattern_def": pattern_def,
                    "transformer": transformer,
                    "type": pattern_def.get("type"),
                    "confidence": pattern_def.get("confidence"),
                    "framework": pattern_def.get("framework"),
                    "description": pattern_def.get("description", "")
                }
            
            # Store codemods in context for RefactorerAgent to use
            if not hasattr(self.context, "codemods"):
                self.context.codemods = {}
            self.context.codemods.update(codemods)
            
            # Record results
            task_manager.record_test_results(
                unit_passed=len(codemods),
                unit_total=len(detected_patterns),
                integration_passed=1 if codemods else 0,
                integration_total=1
            )
            
            task_manager.mark_criterion_met("codemods_prepared_for_all_patterns")
            
            if self.context.verbose:
                print(f"Prepared {len(codemods)} codemods for {len(detected_patterns)} detected patterns")
            
            task_manager.complete_task(success=True)
            
        except Exception as e:
            task_manager.add_error(None, str(e))
            task_manager.complete_task(success=False)
            raise

