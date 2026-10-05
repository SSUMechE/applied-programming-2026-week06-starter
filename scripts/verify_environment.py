"""Check the declared core environment, not student TODO completion."""
import importlib
from importlib.metadata import version
import sys

required = {"pip": "26.2.1", "numpy": "2.4.6", "pytest": "9.1.1", "setuptools": "80.9.0"}
failures = []
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
        importlib.import_module(name)
    except Exception as error:
        failures.append(f"import {name}: {error}")
if failures:
    print("ENVIRONMENT FAIL")
    for failure in failures:
        print(failure)
    raise SystemExit(1)
print("ENVIRONMENT PASS")
