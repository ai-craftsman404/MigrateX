"""
Pattern-to-transformation mapping verification utilities.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re


def verify_pattern_application_mapping(context) -> Dict[str, Any]:
    """
    Verify each detected pattern was attempted for transformation.
    Returns mapping report.
    """
    detected_patterns = context.report.get("patterns", [])
    high_confidence_patterns = [
        p for p in detected_patterns 
        if p.get("confidence") == "high" and p.get("source") == "rule"
    ]
    
    patterns_applied = context.patterns_applied
    updated_files = context.updated_files
    
    # Create mapping: pattern_id → was_applied
    pattern_application_map = {}
    failed_patterns = []
    
    for pattern in high_confidence_patterns:
        pattern_id = pattern.get("id")
        file_path = pattern.get("file")
        module = pattern.get("module", "unknown")
        
        # Check if pattern was applied
        was_applied = pattern_id in patterns_applied
        
        # Check if file was transformed (alternative indicator)
        file_transformed = file_path in updated_files if file_path else False
        
        pattern_application_map[pattern_id] = {
            "detected": True,
            "applied": was_applied,
            "file_transformed": file_transformed,
            "file_path": file_path,
            "module": module
        }
        
        # CRITICAL CHECK: All high-confidence patterns must be applied OR file transformed
        if not was_applied and not file_transformed:
            failed_patterns.append({
                "pattern_id": pattern_id,
                "file": file_path,
                "module": module,
                "reason": "Pattern detected but not applied and file not transformed"
            })
    
    return {
        "pattern_application_map": pattern_application_map,
        "failed_patterns": failed_patterns,
        "total_detected": len(high_confidence_patterns),
        "total_applied": len(patterns_applied),
        "total_files_transformed": len(updated_files),
        "mapping_complete": len(failed_patterns) == 0
    }


def verify_pattern_output_mapping(context) -> List[Dict[str, Any]]:
    """
    Verify each pattern's transformation is correct in output files.
    Returns list of pattern output verification results.
    """
    detected_patterns = context.report.get("patterns", [])
    updated_files = context.updated_files
    
    from migratex.languages.python.patterns import PythonPatterns
    all_patterns = PythonPatterns.get_patterns()
    
    pattern_output_map = []
    
    for pattern in detected_patterns:
        pattern_id = pattern.get("id")
        file_path = pattern.get("file")
        module = pattern.get("module", "")
        confidence = pattern.get("confidence")
        source = pattern.get("source")
        
        # Only verify high-confidence patterns
        if confidence != "high" or source != "rule":
            continue
        
        if not file_path or file_path not in updated_files:
            continue
        
        # Get pattern definition
        pattern_def = None
        for p_key, p_def in all_patterns.items():
            if p_def.get("id") == pattern_id:
                pattern_def = p_def
                break
        
        # Try to find by module if ID doesn't match
        if not pattern_def:
            if module.startswith("semantic_kernel"):
                if "chat_completion" in module or "ChatCompletionAgent" in module:
                    pattern_def = all_patterns.get("sk_import_chat_completion")
                elif "KernelAgent" in module:
                    pattern_def = all_patterns.get("sk_import_agent")
                elif "plugins" in module:
                    pattern_def = all_patterns.get("sk_import_plugins")
                elif "functions" in module:
                    pattern_def = all_patterns.get("sk_import_functions")
            elif module.startswith("autogen"):
                if "ConversableAgent" in module:
                    pattern_def = all_patterns.get("autogen_import_conversable")
                elif "AssistantAgent" in module:
                    pattern_def = all_patterns.get("autogen_import_assistant")
        
        if not pattern_def:
            pattern_output_map.append({
                "pattern_id": pattern_id,
                "file": file_path,
                "status": "error",
                "error": "Pattern definition not found"
            })
            continue
        
        # Read transformed file
        file_path_obj = Path(file_path)
        if not file_path_obj.is_absolute():
            file_path_obj = context.project_path / file_path_obj
        
        try:
            transformed_content = file_path_obj.read_text(encoding="utf-8")
        except Exception as e:
            pattern_output_map.append({
                "pattern_id": pattern_id,
                "file": file_path,
                "status": "error",
                "error": f"Could not read transformed file: {e}"
            })
            continue
        
        # Get original content (from output_dir if exists, otherwise from project_path)
        original_content = ""
        if context.output_dir:
            original_file = context.project_path / file_path_obj.relative_to(context.output_dir)
            if original_file.exists():
                original_content = original_file.read_text(encoding="utf-8")
        else:
            # File was transformed in-place, need to check git diff or backup
            # For now, assume we can't verify original
            original_content = transformed_content  # Will check if pattern was replaced
        
        # Get expected transformation
        expected_pattern = pattern_def.get("pattern")
        expected_replacement = pattern_def.get("replacement")
        
        # Verify transformation
        pattern_in_original = bool(re.search(expected_pattern, original_content)) if original_content else False
        pattern_in_transformed = bool(re.search(expected_pattern, transformed_content))
        replacement_in_transformed = expected_replacement in transformed_content
        
        # Determine transformation status
        if pattern_in_original:
            if pattern_in_transformed and replacement_in_transformed:
                status = "partial"
                error = None
            elif not pattern_in_transformed and replacement_in_transformed:
                status = "success"
                error = None
            elif not pattern_in_transformed and not replacement_in_transformed:
                status = "failed"
                error = "Pattern removed but replacement not found"
            else:
                status = "failed"
                error = "Pattern still present but replacement not found"
        else:
            # Pattern wasn't in original (might be false positive or already transformed)
            if replacement_in_transformed:
                status = "success"  # Replacement already present
                error = None
            else:
                status = "not_found_in_original"
                error = "Pattern detected but not found in original file"
        
        pattern_output_map.append({
            "pattern_id": pattern_id,
            "file": file_path,
            "module": module,
            "status": status,
            "pattern_in_original": pattern_in_original,
            "pattern_in_transformed": pattern_in_transformed,
            "replacement_in_transformed": replacement_in_transformed,
            "expected_replacement": expected_replacement,
            "error": error
        })
    
    return pattern_output_map


def generate_complete_pattern_mapping_report(context) -> Dict[str, Any]:
    """
    Generate complete pattern-to-transformation mapping report.
    """
    # Step 1: Pattern application mapping
    application_result = verify_pattern_application_mapping(context)
    
    # Step 2: Pattern output mapping
    output_map = verify_pattern_output_mapping(context)
    
    # Step 3: Combine into complete report
    successful_outputs = [m for m in output_map if m["status"] == "success"]
    failed_outputs = [m for m in output_map if m["status"] == "failed"]
    
    complete_report = {
        "summary": {
            "patterns_detected": len(context.report.get("patterns", [])),
            "high_confidence_patterns": len([
                p for p in context.report.get("patterns", [])
                if p.get("confidence") == "high" and p.get("source") == "rule"
            ]),
            "patterns_applied": len(context.patterns_applied),
            "files_transformed": len(context.updated_files),
            "pattern_application_rate": (
                len(context.patterns_applied) / len(application_result["pattern_application_map"])
                if application_result["pattern_application_map"] else 0
            ),
            "transformation_success_rate": (
                len(successful_outputs) / len(output_map)
                if output_map else 0
            )
        },
        "pattern_application_mapping": application_result["pattern_application_map"],
        "pattern_output_mapping": output_map,
        "failed_patterns": application_result["failed_patterns"] + failed_outputs,
        "successful_patterns": successful_outputs,
        "mapping_complete": application_result["mapping_complete"] and len(failed_outputs) == 0
    }
    
    return complete_report

