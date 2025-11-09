"""
Outlier Detection System - Detect and classify outlier codebases
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import ast
import re
from collections import Counter


class OutlierDetector:
    """
    Detect and classify outlier codebases.
    Identifies unusual characteristics that may affect migration safety.
    """
    
    def __init__(self):
        self.outlier_types: List[str] = []
        self.risks: List[str] = []
        self.recommendations: List[str] = []
        self.confidence: float = 0.0
    
    def detect_outliers(self, project_path: Path) -> Dict[str, Any]:
        """
        Detect outlier characteristics in codebase.
        
        Returns:
        {
            "is_outlier": bool,
            "outlier_types": List[str],
            "confidence": float,
            "risk_level": str,
            "risks": List[str],
            "recommendations": List[str],
            "details": Dict[str, Any]
        }
        """
        self.outlier_types = []
        self.risks = []
        self.recommendations = []
        
        details = {}
        
        # Detect structure outliers
        structure_outliers = self._detect_structure_outliers(project_path)
        if structure_outliers:
            self.outlier_types.extend(structure_outliers["types"])
            self.risks.extend(structure_outliers["risks"])
            self.recommendations.extend(structure_outliers["recommendations"])
            details["structure"] = structure_outliers
        
        # Detect code outliers
        code_outliers = self._detect_code_outliers(project_path)
        if code_outliers:
            self.outlier_types.extend(code_outliers["types"])
            self.risks.extend(code_outliers["risks"])
            self.recommendations.extend(code_outliers["recommendations"])
            details["code"] = code_outliers
        
        # Detect pattern outliers
        pattern_outliers = self._detect_pattern_outliers(project_path)
        if pattern_outliers:
            self.outlier_types.extend(pattern_outliers["types"])
            self.risks.extend(pattern_outliers["risks"])
            self.recommendations.extend(pattern_outliers["recommendations"])
            details["patterns"] = pattern_outliers
        
        # Detect size outliers
        size_outliers = self._detect_size_outliers(project_path)
        if size_outliers:
            self.outlier_types.extend(size_outliers["types"])
            self.risks.extend(size_outliers["risks"])
            self.recommendations.extend(size_outliers["recommendations"])
            details["size"] = size_outliers
        
        # Calculate confidence and risk level
        self.confidence = self._calculate_confidence()
        risk_level = self._calculate_risk_level()
        
        is_outlier = len(self.outlier_types) > 0
        
        return {
            "is_outlier": is_outlier,
            "outlier_types": list(set(self.outlier_types)),  # Remove duplicates
            "confidence": self.confidence,
            "risk_level": risk_level,
            "risks": list(set(self.risks)),
            "recommendations": list(set(self.recommendations)),
            "details": details
        }
    
    def _detect_structure_outliers(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Detect structural outliers."""
        outliers = {"types": [], "risks": [], "recommendations": []}
        
        # Check for monorepo (multiple projects)
        project_dirs = [d for d in project_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        # Check if multiple have Python files (monorepo detection)
        python_project_count = sum(
            1 for d in project_dirs 
            if any(d.rglob("*.py"))
        )
        if python_project_count > 1:
            outliers["types"].append("monorepo")
            outliers["risks"].append("Multiple projects may have different migration requirements")
            outliers["recommendations"].append("Consider migrating each project separately")
        
        # Check for deep nesting
        max_depth = self._calculate_max_depth(project_path)
        if max_depth > 10:
            outliers["types"].append("deep_nesting")
            outliers["risks"].append("Deep nesting may cause path resolution issues")
            outliers["recommendations"].append("Verify path handling for deeply nested files")
        
        # Check for generated code directories
        generated_dirs = ["generated", "build", "dist", "__pycache__", ".pytest_cache"]
        if any((project_path / d).exists() for d in generated_dirs):
            outliers["types"].append("generated_code")
            outliers["risks"].append("Generated code should not be migrated")
            outliers["recommendations"].append("Exclude generated code directories from migration")
        
        # Check for git submodules
        if (project_path / ".gitmodules").exists():
            outliers["types"].append("git_submodules")
            outliers["risks"].append("Submodules may have different migration requirements")
            outliers["recommendations"].append("Handle submodules separately")
        
        # Check for namespace packages
        namespace_packages = self._detect_namespace_packages(project_path)
        if namespace_packages:
            outliers["types"].append("namespace_packages")
            outliers["risks"].append("Namespace packages require special handling")
            outliers["recommendations"].append("Verify namespace package migration")
        
        return outliers if outliers["types"] else None
    
    def _detect_code_outliers(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Detect code-level outliers."""
        outliers = {"types": [], "risks": [], "recommendations": []}
        
        python_files = list(project_path.rglob("*.py"))
        if not python_files:
            return None
        
        large_files = []
        large_functions = []
        deep_nesting = []
        mixed_indentation = []
        encoding_issues = []
        
        for file_path in python_files:
            # Skip common directories
            if any(part in file_path.parts for part in ["__pycache__", ".git", "venv", "env"]):
                continue
            
            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.splitlines()
                
                # Check file size
                if len(lines) > 10000:
                    large_files.append(str(file_path.relative_to(project_path)))
                    outliers["types"].append("large_files")
                
                # Check for mixed indentation
                has_tabs = any('\t' in line for line in lines[:100])
                has_spaces = any(line.startswith(' ') for line in lines[:100])
                if has_tabs and has_spaces:
                    mixed_indentation.append(str(file_path.relative_to(project_path)))
                    outliers["types"].append("mixed_indentation")
                
                # Check encoding issues
                try:
                    file_path.read_bytes().decode("utf-8")
                except UnicodeDecodeError:
                    encoding_issues.append(str(file_path.relative_to(project_path)))
                    outliers["types"].append("encoding_issues")
                
                # Parse AST for code structure analysis
                try:
                    tree = ast.parse(content, filename=str(file_path))
                    max_func_lines, max_nesting = self._analyze_code_structure(tree, content)
                    
                    if max_func_lines > 1000:
                        large_functions.append(str(file_path.relative_to(project_path)))
                        outliers["types"].append("large_functions")
                    
                    if max_nesting > 20:
                        deep_nesting.append(str(file_path.relative_to(project_path)))
                        outliers["types"].append("deep_nesting")
                        
                except SyntaxError:
                    # Syntax errors are handled separately
                    pass
                    
            except Exception as e:
                # Skip files that can't be read
                continue
        
        # Add risks and recommendations
        if large_files:
            outliers["risks"].append(f"{len(large_files)} very large files (>10K lines) may cause performance issues")
            outliers["recommendations"].append("Consider splitting large files before migration")
        
        if large_functions:
            outliers["risks"].append(f"{len(large_functions)} files with very large functions (>1000 lines)")
            outliers["recommendations"].append("Large functions may need manual review")
        
        if mixed_indentation:
            outliers["risks"].append(f"{len(mixed_indentation)} files with mixed indentation (tabs/spaces)")
            outliers["recommendations"].append("Normalize indentation before migration")
        
        if encoding_issues:
            outliers["risks"].append(f"{len(encoding_issues)} files with encoding issues")
            outliers["recommendations"].append("Fix encoding issues before migration")
        
        return outliers if outliers["types"] else None
    
    def _detect_pattern_outliers(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Detect pattern-related outliers."""
        outliers = {"types": [], "risks": [], "recommendations": []}
        
        python_files = list(project_path.rglob("*.py"))
        unusual_contexts = []
        unusual_file_types = []
        
        for file_path in python_files:
            # Skip common directories
            if any(part in file_path.parts for part in ["__pycache__", ".git", "venv", "env"]):
                continue
            
            # Check file type
            if file_path.suffix in [".pyi", ".pyw"]:
                unusual_file_types.append(str(file_path.relative_to(project_path)))
                outliers["types"].append("unusual_file_types")
            
            # Check for patterns in unusual contexts (simplified check)
            try:
                content = file_path.read_text(encoding="utf-8")
                
                # Check if patterns appear only in comments/strings
                if self._patterns_only_in_comments(content):
                    unusual_contexts.append(str(file_path.relative_to(project_path)))
                    outliers["types"].append("patterns_in_comments")
                    
            except Exception:
                continue
        
        if unusual_file_types:
            outliers["risks"].append(f"{len(unusual_file_types)} unusual file types (.pyi, .pyw) may need special handling")
            outliers["recommendations"].append("Review unusual file types manually")
        
        if unusual_contexts:
            outliers["risks"].append(f"{len(unusual_contexts)} files with patterns only in comments")
            outliers["recommendations"].append("Verify pattern detection in these files")
        
        return outliers if outliers["types"] else None
    
    def _detect_size_outliers(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Detect size-related outliers."""
        outliers = {"types": [], "risks": [], "recommendations": []}
        
        python_files = list(project_path.rglob("*.py"))
        total_files = len(python_files)
        
        # Very large codebase
        if total_files > 10000:
            outliers["types"].append("very_large_codebase")
            outliers["risks"].append(f"Very large codebase ({total_files} files) may cause performance issues")
            outliers["recommendations"].append("Consider migrating in batches or using --output-dir")
        
        # Very small codebase
        elif total_files < 5:
            outliers["types"].append("very_small_codebase")
            outliers["risks"].append("Very small codebase may not represent typical usage")
            outliers["recommendations"].append("Verify migration completeness")
        
        # Extreme file size variations
        if python_files:
            file_sizes = []
            for f in python_files[:100]:
                try:
                    content = f.read_text(encoding="utf-8")
                    file_sizes.append(len(content.splitlines()))
                except UnicodeDecodeError:
                    # Handle non-UTF-8 files gracefully
                    try:
                        # Try latin-1 as fallback
                        content = f.read_text(encoding="latin-1")
                        file_sizes.append(len(content.splitlines()))
                    except Exception:
                        # Skip files that can't be read
                        continue
            if file_sizes:
                max_size = max(file_sizes)
                min_size = min(file_sizes)
                if max_size > 0 and min_size > 0:
                    size_ratio = max_size / min_size
                    if size_ratio > 1000:
                        outliers["types"].append("extreme_size_variation")
                        outliers["risks"].append("Extreme file size variations may affect migration consistency")
                        outliers["recommendations"].append("Review file size distribution")
        
        return outliers if outliers["types"] else None
    
    def _calculate_max_depth(self, project_path: Path) -> int:
        """Calculate maximum directory nesting depth."""
        max_depth = 0
        for item in project_path.rglob("*"):
            if item.is_dir():
                depth = len(item.relative_to(project_path).parts)
                max_depth = max(max_depth, depth)
        return max_depth
    
    def _detect_namespace_packages(self, project_path: Path) -> bool:
        """Detect if codebase uses namespace packages."""
        # Check for namespace package indicators
        for py_file in project_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                content = py_file.read_text(encoding="utf-8")
                # Simple heuristic: empty __init__.py in nested structure
                if not content.strip() and len(py_file.parts) > 3:
                    return True
        return False
    
    def _analyze_code_structure(self, tree: ast.AST, content: str) -> tuple[int, int]:
        """Analyze code structure for function size and nesting depth."""
        max_func_lines = 0
        max_nesting = 0
        
        class NestingVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_nesting = 0
                self.max_nesting = 0
                self.function_lines = {}
            
            def visit_FunctionDef(self, node):
                # Calculate function lines
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    func_lines = node.end_lineno - node.lineno if node.end_lineno else 1
                    self.function_lines[node.name] = func_lines
                
                # Track nesting
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
        
        max_func_lines = max(visitor.function_lines.values()) if visitor.function_lines else 0
        max_nesting = visitor.max_nesting
        
        return max_func_lines, max_nesting
    
    def _patterns_only_in_comments(self, content: str) -> bool:
        """Check if SK/AutoGen patterns appear only in comments."""
        # Simple heuristic: check if patterns appear but not as actual imports
        sk_pattern = r"semantic[_\s]*kernel"
        autogen_pattern = r"autogen"
        
        has_sk_comment = bool(re.search(rf"#.*{sk_pattern}", content, re.IGNORECASE))
        has_autogen_comment = bool(re.search(rf"#.*{autogen_pattern}", content, re.IGNORECASE))
        
        has_sk_import = bool(re.search(rf"from\s+{sk_pattern}|import\s+{sk_pattern}", content, re.IGNORECASE))
        has_autogen_import = bool(re.search(rf"from\s+{autogen_pattern}|import\s+{autogen_pattern}", content, re.IGNORECASE))
        
        # If patterns in comments but no actual imports
        return (has_sk_comment or has_autogen_comment) and not (has_sk_import or has_autogen_import)
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence score for outlier detection."""
        # More outlier types = higher confidence
        base_confidence = min(len(self.outlier_types) * 0.2, 1.0)
        return base_confidence
    
    def _calculate_risk_level(self) -> str:
        """Calculate overall risk level."""
        critical_types = ["very_large_codebase", "encoding_issues", "git_submodules"]
        high_types = ["monorepo", "large_files", "large_functions", "deep_nesting"]
        medium_types = ["mixed_indentation", "unusual_file_types", "patterns_in_comments"]
        
        if any(t in self.outlier_types for t in critical_types):
            return "critical"
        elif any(t in self.outlier_types for t in high_types):
            return "high"
        elif any(t in self.outlier_types for t in medium_types):
            return "medium"
        elif self.outlier_types:
            return "low"
        else:
            return "none"

