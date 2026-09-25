# Testing convention

A test names one behavior and shows the condition that makes it true or false. The expected result comes from a contract, a fixed fixture, an independent implementation, or an invariant. Do not compute the expectation by calling the code under test again. A comparison between two outputs is useful when it tests a stated relationship between them.

Check the public result and the state at risk: a catalog row, file bytes, destination name, export, or absence of a write. A refusal pins the applicable exit code or exception, the specific error code, and the unchanged state that matters. Keep setup failures visible so the named operation is actually reached.

Change one relevant input to show why the outcome changes. [The duplicate attachment test](../tests/contract/test_duplicate_attachment.py) changes file content while holding the other facts steady. Inject faults at named boundaries and inspect persisted state after retry, as [the interrupted export test](../tests/contract/test_skeleton_export.py) does. Test a command through its CLI when the promise includes parsing, exit status, or the result envelope, as [the unsupported input test](../tests/contract/test_capture.py) does.

A generator needs an invariant that can fail on a wrong result and a small, saved fixture for each real defect it discovers. A test may fail when its setup or dependencies break; its assertions should still distinguish the behavior it names from a mere absence of a crash. Keep cases that guard distinct behavior, even when a nearby assertion needs repair.

## Coverage run

The full suite runs in parallel with `uv run --locked pytest`. Use `uv run --locked pytest -m "not slow"` for the inner loop; `slow` names the installed smoke test, the five-second lock wait, and tests that invoke external rendering tools. Use `uv run --locked pytest -n 0` when a serial run is needed.

The ordinary test run does not start subprocess coverage. From the repository root, run `COVERAGE_PROCESS_START="$PWD/.coveragerc" PYTHONPATH="$PWD/tests/coverage_bootstrap${PYTHONPATH:+:$PYTHONPATH}" uv run --locked coverage run -m pytest`, then `uv run --locked coverage combine` and `uv run --locked coverage report`. This measures the Python CLI subprocesses as well as the test process. Coverage is a data point, not a gate.
