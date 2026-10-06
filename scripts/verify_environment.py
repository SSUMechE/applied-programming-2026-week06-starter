"""Check the declared core environment, not student TODO completion."""
import importlib
from importlib.metadata import version
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
required = {"pip": "26.2.1", "numpy": "2.4.6", "pytest": "9.1.1", "setuptools": "80.9.0"}
failures = []
checkout_problem = False
if sys.version_info[:3] != (3, 12, 13):
    failures.append(f"Python expected 3.12.13, found {sys.version.split()[0]}")
for name, expected in required.items():
    try:
        actual = version(name)
        if actual != expected:
            failures.append(f"{name} expected {expected}, found {actual}")
    except Exception as error:
        failures.append(f"{name}: {error}")
for name in ("numpy", "pytest", "ap_week06"):
    try:
        module = importlib.import_module(name)
        if name == "ap_week06":
            loaded_file = getattr(module, "__file__", None)
            loaded = Path(loaded_file).resolve() if loaded_file else None
            expected = ROOT / "src" / "ap_week06" / "__init__.py"
            if loaded != expected.resolve():
                checkout_problem = True
                failures.extend([
                    "ap_week06 is loaded from a different repository.",
                    f"Loaded: {loaded}",
                    f"Expected: {expected}",
                ])
    except Exception as error:
        failures.append(f"import {name}: {error}")
        if name == "ap_week06":
            checkout_problem = True
if failures:
    print("ENVIRONMENT FAIL")
    for failure in failures:
        print(failure)
    if checkout_problem:
        print("In Anaconda Prompt, activate applied-programming-w06, then run:")
        print(f'cd /d "{ROOT}"')
        print("python -m pip install -e . --no-build-isolation")
        print("python scripts/verify_environment.py")
    raise SystemExit(1)
print("ENVIRONMENT PASS")
