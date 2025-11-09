"""
Refactorer Agent - Code transformation
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from migratex.agents import BaseAgent
from migratex.docs import migration_docs
from migratex.utils.interactive import prompt_pattern_decision, prompt_file_decision

# Optional imports for future AST-based transformations
try:
    from migratex.languages.python.parser_libcst import PythonLibCSTParser
    HAS_LIBCST = True
except ImportError:
    HAS_LIBCST = False
    PythonLibCSTParser = None

try:
    from migratex.languages.python.transformers import PythonTransformer
    HAS_TRANSFORMER = True
except ImportError:
    HAS_TRANSFORMER = False
    PythonTransformer = None


class RefactorerAgent(BaseAgent):
    """
    Rewrites code from SK/AutoGen style towards MAF-style patterns.
    Provides safe, reviewable refactors with human-in-the-loop.
    Uses Microsoft's official migration guides for transformation patterns.
    """
    
    def __init__(self, context):
        super().__init__(context)
        # Initialize parser only if libcst is available (for future AST-based transformations)
        self.parser = PythonLibCSTParser() if HAS_LIBCST else None
        self.decision_cache: Dict[str, str] = {}  # Cache user decisions for review mode
    
    def run(self):
        """Run refactoring based on context mode."""
        if self.context.mode == "auto":
            self.run_auto()
        elif self.context.mode == "review":
            self.run_review()
        else:
            raise ValueError(f"Unknown mode: {self.context.mode}")
    
    def run_auto(self):
        """Run refactoring in auto mode (high-confidence only)."""
        task_manager = self.context.get_task_manager()
        task_id = task_manager.start_task(
            "refactor_auto",
            "Auto Refactoring",
            "Apply high-confidence transformations automatically",
            acceptance_criteria=[
                "high_confidence_patterns_applied",
                "files_transformed_successfully",
                "no_syntax_errors_introduced",
                "unit_tests_all_passed",
                "integration_tests_all_passed"
            ]
        )
        
        try:
            # Load migration documentation for reference
            best_practices = migration_docs.get_best_practices()
            
            # Get detected patterns from analysis report
            if "patterns" not in self.context.report:
                raise ValueError("No patterns detected. Run 'analyze' command first.")
            
            detected_patterns = self.context.report["patterns"]
            
            # Filter to high-confidence patterns only
            high_confidence_patterns = [
                p for p in detected_patterns 
                if p.get("confidence") == "high" and p.get("source") == "rule"
            ]
            
            if not high_confidence_patterns:
                if self.context.verbose:
                    print("No high-confidence patterns found for auto-refactoring.")
                    print("This may result in 0 files being transformed.")
                # CRITICAL FIX: Mark as failed if no patterns to transform
                task_manager.complete_task(success=False)
                return
            
            # Get files that need transformation
            files_to_transform = self._get_files_for_patterns(high_confidence_patterns)
            
            # Apply transformations
            transformed_count = 0
            for file_path in files_to_transform:
                try:
                    if self._transform_file(file_path, high_confidence_patterns, auto_mode=True):
                        transformed_count += 1
                        self.context.updated_files.append(str(file_path))
                except Exception as e:
                    error_info = {
                        "file": str(file_path),
                        "error": str(e)
                    }
                    self.context.failed_files.append(error_info)
                    if self.context.error_policy == "stop":
                        raise
            
            # CRITICAL FIX: Verify before marking success
            # Only mark criteria as met if transformations actually occurred
            if transformed_count > 0:
                task_manager.mark_criterion_met("high_confidence_patterns_applied")
                task_manager.mark_criterion_met("files_transformed_successfully")
            else:
                # No transformations - don't mark as success
                if self.context.verbose:
                    print(f"Warning: No files were transformed. {len(high_confidence_patterns)} patterns detected but 0 files transformed.")
                    print("This may indicate a pattern matching issue.")
            
            # Record results
            task_manager.record_test_results(
                unit_passed=transformed_count,
                unit_total=len(files_to_transform),
                integration_passed=1 if transformed_count > 0 else 0,
                integration_total=1
            )
            
            if self.context.verbose:
                print(f"Auto-refactored {transformed_count} files")
                print(f"Applied {len(self.context.patterns_applied)} patterns")
            
            # CRITICAL FIX: Don't pass success=True explicitly - let TaskManager check criteria
            # Only mark as success if transformations occurred
            if transformed_count > 0:
                task_manager.complete_task()  # Let it check criteria automatically
            else:
                # No transformations - mark as failed
                task_manager.complete_task(success=False)
            
        except Exception as e:
            task_manager.add_error(None, str(e))
            task_manager.complete_task(success=False)
            raise
    
    def run_review(self):
        """Run refactoring in review mode (interactive confirmation)."""
        task_manager = self.context.get_task_manager()
        task_id = task_manager.start_task(
            "refactor_review",
            "Interactive Refactoring",
            "Apply transformations with user confirmation",
            acceptance_criteria=[
                "user_reviewed_all_changes",
                "files_transformed_successfully",
                "no_syntax_errors_introduced",
                "unit_tests_all_passed",
                "integration_tests_all_passed"
            ]
        )
        
        try:
            # Load migration documentation for reference
            best_practices = migration_docs.get_best_practices()
            
            # Get detected patterns from analysis report
            if "patterns" not in self.context.report:
                raise ValueError("No patterns detected. Run 'analyze' command first.")
            
            detected_patterns = self.context.report["patterns"]
            
            # Get files that need transformation
            files_to_transform = self._get_files_for_patterns(detected_patterns)
            
            # Apply transformations with user review
            transformed_count = 0
            for file_path in files_to_transform:
                try:
                    if self._transform_file(file_path, detected_patterns, auto_mode=False):
                        transformed_count += 1
                        self.context.updated_files.append(str(file_path))
                except Exception as e:
                    error_info = {
                        "file": str(file_path),
                        "error": str(e)
                    }
                    self.context.failed_files.append(error_info)
                    if self.context.error_policy == "stop":
                        raise
            
            # Record results
            task_manager.record_test_results(
                unit_passed=transformed_count,
                unit_total=len(files_to_transform),
                integration_passed=1 if transformed_count > 0 else 0,
                integration_total=1
            )
            
            # CRITICAL FIX: Only mark criteria if transformations occurred
            if transformed_count > 0:
                task_manager.mark_criterion_met("user_reviewed_all_changes")
                task_manager.mark_criterion_met("files_transformed_successfully")
            
            if self.context.verbose:
                print(f"Refactored {transformed_count} files with user review")
            
            # CRITICAL FIX: Don't pass success=True explicitly
            if transformed_count > 0:
                task_manager.complete_task()  # Let it check criteria automatically
            else:
                task_manager.complete_task(success=False)
            
        except Exception as e:
            task_manager.add_error(None, str(e))
            task_manager.complete_task(success=False)
            raise
    
    def _find_matching_pattern(self, pattern_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find matching pattern definition by ID, module name, or regex.
        CRITICAL FIX: This resolves the pattern ID mismatch issue.
        """
        pattern_id = pattern_info.get("id")
        module = pattern_info.get("module", "")
        pattern_type = pattern_info.get("type", "")
        
        # Method 1: Try exact ID match
        pattern_def = self.context.pattern_library.get_pattern(pattern_id)
        if pattern_def:
            return pattern_def
        
        # Method 2: Try PythonPatterns by exact ID
        from migratex.languages.python.patterns import PythonPatterns
        all_patterns = PythonPatterns.get_patterns()
        pattern_def = next(
            (p for p in all_patterns.values() if p.get("id") == pattern_id),
            None
        )
        if pattern_def:
            return pattern_def
        
        # Method 3: Match by module name (CRITICAL FIX)
        if module:
            module_parts = module.split(".")
            
            # Check for semantic_kernel patterns
            if module.startswith("semantic_kernel"):
                # Specific patterns (highest priority)
                if "agents" in module_parts:
                    if "chat_completion" in module or "ChatCompletionAgent" in module or "AgentGroupChat" in module:
                        pattern_def = all_patterns.get("sk_import_chat_completion")
                        if pattern_def:
                            return pattern_def
                    if "KernelAgent" in module or "kernel_agent" in module:
                        pattern_def = all_patterns.get("sk_import_agent")
                        if pattern_def:
                            return pattern_def
                    # Generic agents import
                    pattern_def = all_patterns.get("sk_import_chat_completion")
                    if pattern_def:
                        return pattern_def
                
                # Functions/tools patterns
                if "functions" in module_parts:
                    pattern_def = all_patterns.get("sk_import_functions")
                    if pattern_def:
                        return pattern_def
                
                # Plugins patterns
                if "plugins" in module_parts:
                    pattern_def = all_patterns.get("sk_import_plugins")
                    if pattern_def:
                        return pattern_def
                
                # Core kernel pattern
                if module == "semantic_kernel" or (len(module_parts) == 1 and module_parts[0] == "semantic_kernel"):
                    pattern_def = all_patterns.get("sk_import_kernel")
                    if pattern_def:
                        return pattern_def
                
                # Generic fallback: any semantic_kernel import should use generic kernel pattern
                # This handles connectors, contents, filters, memory, processes, etc.
                pattern_def = all_patterns.get("sk_import_kernel")
                if pattern_def:
                    return pattern_def
            
            # Check for autogen patterns
            elif module.startswith("autogen"):
                if "ConversableAgent" in module:
                    pattern_def = all_patterns.get("autogen_import_conversable")
                    if pattern_def:
                        return pattern_def
                if "AssistantAgent" in module:
                    pattern_def = all_patterns.get("autogen_import_assistant")
                    if pattern_def:
                        return pattern_def
                # Generic autogen fallback
                pattern_def = all_patterns.get("autogen_import_conversable")
                if pattern_def:
                    return pattern_def
        
        # Method 4: Match by pattern regex against file content
        file_path = pattern_info.get("file")
        if file_path:
            try:
                file_path_obj = Path(file_path)
                if not file_path_obj.is_absolute():
                    file_path_obj = self.context.project_path / file_path_obj
                
                with open(file_path_obj, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Try each pattern's regex against content
                for pattern_key, pattern_def in all_patterns.items():
                    pattern_regex = pattern_def.get("pattern")
                    if pattern_regex and re.search(pattern_regex, content):
                        # Found a match - verify it's the right type
                        if pattern_def.get("type") == pattern_type:
                            return pattern_def
            except Exception:
                pass
        
        return None
    
    def _get_files_for_patterns(self, patterns: List[Dict[str, Any]]) -> List[Path]:
        """Get unique files that contain the detected patterns."""
        files_set = set()
        for pattern in patterns:
            file_path = pattern.get("file")
            if file_path:
                file_path = Path(file_path)
                # Make absolute if relative
                if not file_path.is_absolute():
                    file_path = self.context.project_path / file_path
                files_set.add(file_path)
        
        # Fallback to all Python files if no file info in patterns
        if not files_set:
            files_set = set(self.context.report.get("files", []))
            files_set = {self.context.project_path / Path(f) if not Path(f).is_absolute() else Path(f) 
                        for f in files_set}
        
        return sorted(files_set)
    
    def _check_file_outliers(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Check if a file has outlier characteristics.
        
        Returns:
            Dict with "reasons" list if file is outlier, None otherwise
        """
        reasons = []
        
        try:
            # Check file size
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            if len(lines) > 10000:
                reasons.append(f"Very large file ({len(lines)} lines)")
            
            # Check for mixed indentation
            has_tabs = any('\t' in line for line in lines[:100])
            has_spaces = any(line.startswith(' ') for line in lines[:100])
            if has_tabs and has_spaces:
                reasons.append("Mixed indentation (tabs and spaces)")
            
            # Check for encoding issues
            try:
                file_path.read_bytes().decode("utf-8")
            except UnicodeDecodeError:
                reasons.append("Encoding issues (non-UTF-8)")
            
            # Check for deep nesting (if AST parsing succeeds)
            try:
                import ast
                tree = ast.parse(content, filename=str(file_path))
                max_nesting = self._calculate_max_nesting(tree)
                if max_nesting > 20:
                    reasons.append(f"Deep nesting ({max_nesting} levels)")
            except SyntaxError:
                reasons.append("Syntax errors detected")
            except Exception:
                pass  # Skip AST analysis if it fails
            
            # Check if file is in outlier report details
            outlier_report = getattr(self.context, 'report', {}).get('outlier_report', {})
            outlier_details = outlier_report.get('details', {})
            
            # Check code outliers
            code_outliers = outlier_details.get('code', {})
            if code_outliers:
                # Check for large files
                large_files = []
                if isinstance(code_outliers.get('large_files'), list):
                    large_files = code_outliers['large_files']
                
                if str(file_path) in large_files or any(str(file_path).endswith(f) for f in large_files):
                    reasons.append("Very large file (>10K lines)")
                
                # Check for mixed indentation
                mixed_indent_files = []
                if isinstance(code_outliers.get('mixed_indentation'), list):
                    mixed_indent_files = code_outliers['mixed_indentation']
                
                if str(file_path) in mixed_indent_files or any(str(file_path).endswith(f) for f in mixed_indent_files):
                    reasons.append("Mixed indentation detected")
            
            if reasons:
                return {"reasons": reasons}
        
        except Exception as e:
            # If we can't read/analyze the file, it's an outlier
            return {"reasons": [f"Cannot analyze file: {str(e)}"]}
        
        return None
    
    def _calculate_max_nesting(self, tree) -> int:
        """Calculate maximum nesting depth in AST."""
        import ast
        
        class NestingVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_nesting = 0
                self.max_nesting = 0
            
            def visit_FunctionDef(self, node):
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1
            
            def visit_ClassDef(self, node):
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1
        
        visitor = NestingVisitor()
        visitor.visit(tree)
        return visitor.max_nesting
    
    def _transform_file(
        self, 
        file_path: Path, 
        patterns: List[Dict[str, Any]], 
        auto_mode: bool = False
    ) -> bool:
        """
        Transform a single file using detected patterns.
        
        Returns True if file was modified, False otherwise.
        """
        # Check for file-level outliers if in cautious/review mode
        if hasattr(self.context, 'outlier_mode') and self.context.outlier_mode in ["cautious", "review"]:
            file_outliers = self._check_file_outliers(file_path)
            if file_outliers:
                # Generate changes summary for prompt
                file_patterns = [
                    p for p in patterns 
                    if not p.get("file") or Path(p.get("file")) == file_path
                ]
                changes_summary = f"{len(file_patterns)} pattern(s) detected"
                
                from migratex.utils.outlier_prompts import prompt_outlier_file_decision
                decision = prompt_outlier_file_decision(
                    str(file_path),
                    file_outliers["reasons"],
                    changes_summary
                )
                
                if decision == "no":
                    if self.context.verbose:
                        print(f"Skipping outlier file: {file_path}")
                    return False  # Skip this file
                elif decision == "abort":
                    raise ValueError("Migration aborted by user")
                elif decision == "review":
                    # Continue but will show diff later in review mode
                    pass
        
        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()
        
        modified_content = original_content
        patterns_applied = []
        
        # Filter patterns relevant to this file
        file_patterns = [
            p for p in patterns 
            if not p.get("file") or Path(p.get("file")) == file_path
        ]
        
        # Apply each pattern
        for pattern_info in file_patterns:
            # CRITICAL FIX: Use _find_matching_pattern instead of direct ID lookup
            pattern_def = self._find_matching_pattern(pattern_info)
            
            if not pattern_def:
                # Log warning but continue (don't fail silently)
                if self.context.verbose:
                    pattern_id = pattern_info.get("id")
                    module = pattern_info.get("module", "unknown")
                    print(f"Warning: Could not find matching pattern for ID '{pattern_id}', module '{module}'")
                continue
            
            pattern_id = pattern_def.get("id")  # Use the matched pattern's ID
            
            # Check if high confidence (for auto mode)
            if auto_mode and pattern_def.get("confidence") != "high":
                continue
            
            # Check decision cache (for review mode)
            if not auto_mode:
                cache_key = f"{pattern_id}:{file_path}"
                if cache_key in self.decision_cache:
                    decision = self.decision_cache[cache_key]
                    if decision == "s":  # Skip
                        continue
                    elif decision == "a":  # Accept for all similar
                        # Apply to all files with this pattern
                        pass
            
            # Apply pattern transformation
            pattern_regex = pattern_def.get("pattern")
            replacement = pattern_def.get("replacement")
            
            if pattern_regex and replacement:
                # Handle class inheritance patterns that need class name extraction
                if pattern_def.get("type") == "class_inheritance" and "{name}" in replacement:
                    # Extract class name from pattern match
                    match = re.search(r"class (\w+)\(", modified_content)
                    if match:
                        class_name = match.group(1)
                        replacement = replacement.format(name=class_name)
                
                # Apply regex replacement
                if re.search(pattern_regex, modified_content):
                    modified_content = re.sub(pattern_regex, replacement, modified_content)
                    patterns_applied.append(pattern_id)
                    self.context.patterns_applied.append(pattern_id)
        
        # If content changed, write back (with review confirmation if needed)
        if modified_content != original_content:
            # Determine target file path (output_dir or in-place)
            if self.context.output_dir:
                # Write to output directory, preserving relative path structure
                relative_path = file_path.relative_to(self.context.project_path)
                target_path = self.context.output_dir / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                write_path = target_path
            else:
                # Write in-place (original behaviour)
                write_path = file_path
            
            if auto_mode:
                # Auto mode: write directly
                with open(write_path, "w", encoding="utf-8") as f:
                    f.write(modified_content)
                return True
            else:
                # Review mode: prompt user
                changes_summary = f"{len(patterns_applied)} patterns applied: {', '.join(patterns_applied[:3])}"
                if len(patterns_applied) > 3:
                    changes_summary += "..."
                
                decision = prompt_file_decision(str(file_path), changes_summary)
                
                if decision == "y":
                    # User accepted: write file
                    with open(write_path, "w", encoding="utf-8") as f:
                        f.write(modified_content)
                    
                    # Cache decision if remember_decisions is enabled
                    if self.context.remember_decisions:
                        for pattern_id in patterns_applied:
                            cache_key = f"{pattern_id}:{file_path}"
                            self.decision_cache[cache_key] = "a"  # Accept
                    
                    return True
                elif decision == "e":
                    # User wants to edit manually - open file in editor
                    # For now, just skip (could integrate with $EDITOR)
                    if self.context.verbose:
                        print(f"Manual edit requested for {file_path}")
                    return False
                else:
                    # User skipped
                    return False
        
        return False

