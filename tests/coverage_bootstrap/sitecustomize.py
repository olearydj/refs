"""Start coverage in child interpreters only during the explicit coverage run."""

import os

if os.environ.get("COVERAGE_PROCESS_START"):
    import coverage

    coverage.process_startup()
