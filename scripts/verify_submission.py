"""Check protected files, editable boundaries and executable local completion.

This checks files and tests on this PC. It does not verify GitHub access, the
pushed commit, LMS submission, every possible program input.
"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def structure(path, allowed):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in allowed:
            node.body = [ast.Pass()]
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if f"{node.name}.{item.name}" in allowed:
                        item.body = [ast.Pass()]
    return hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()


def main():
    manifest = json.loads((ROOT / "protected_manifest.json").read_text(encoding="utf-8"))
    problems = []
    for name, expected in manifest["protected"].items():
        path = ROOT / name
        if not path.is_file():
            problems.append(f"missing protected file: {name}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            problems.append(f"protected file changed: {name}")
    for name, specification in manifest["editable"].items():
        try:
            actual = structure(ROOT / name, specification["allowed_bodies"])
            if actual != specification["structure_sha256"]:
                problems.append(f"changed outside the permitted bodies: {name}")
        except (OSError, SyntaxError) as error:
            problems.append(f"cannot read {name}: {error}")
    if problems:
        print("LOCAL CHECK FAIL")
        for problem in problems:
            print(problem)
        return 1
    result = subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "tests/public",
                             "tests/test_student.py", "-q"], cwd=ROOT)
    if result.returncode:
        print("LOCAL CHECK FAIL: tests did not all pass")
        return 1
    print("LOCAL CHECK PASS")
    print("Files and tests checked. GitHub and LMS are separate checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
