"""The narrated demonstration is the single installed end-to-end test."""

import subprocess


def test_installed_smoke():
    result = subprocess.run(['scripts/demo.sh', '--smoke'], capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS refs demo: 121 checks' in result.stdout
