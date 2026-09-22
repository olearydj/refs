import os
import subprocess


def test_help_without_data_access():
    assert os.access('scripts/demo.sh', os.X_OK)
    result = subprocess.run(['scripts/demo.sh', '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stderr == ''
    for option in ['--smoke', '--no-pause', '--keep']:
        assert option in result.stdout


def test_unknown_option_before_data_access():
    result = subprocess.run(['scripts/demo.sh', '--not-an-option'], capture_output=True, text=True)
    assert result.returncode == 2
    assert result.stdout == ''
    assert 'error: unknown option: --not-an-option' in result.stderr
