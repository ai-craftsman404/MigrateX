"""Count test methods in test files"""
from pathlib import Path
import re

test_dirs = {
    "unit": Path("tests/unit"),
    "integration": Path("tests/integration"),
    "e2e": Path("tests/e2e"),
    "edge_cases": Path("tests/edge_cases"),
    "outliers": Path("tests/outliers"),
    "performance": Path("tests/performance"),
    "error_recovery": Path("tests/error_recovery"),
    "transformation": Path("tests/transformation"),
    "pattern_detection": Path("tests/pattern_detection")
}

print("Test Coverage Summary\n" + "="*60)

total_tests = 0
for category, test_dir in test_dirs.items():
    if not test_dir.exists():
        continue
    
    test_files = list(test_dir.rglob("test_*.py"))
    category_total = 0
    
    print(f"\n{category.upper()} Tests:")
    for test_file in sorted(test_files):
        content = test_file.read_text()
        test_methods = re.findall(r'def test_\w+', content)
        count = len(test_methods)
        category_total += count
        print(f"  - {test_file.name}: {count} tests")
    
    if category_total > 0:
        print(f"  Category Total: {category_total} tests")
        total_tests += category_total

print(f"\n{'='*60}")
print(f"GRAND TOTAL: {total_tests} tests")
print(f"{'='*60}")
