"""The private-input trial refuses early when its owner-supplied files are absent."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize('script', ['run.sh', 'isolated_trial.py'])
def test_real_trial_names_missing_private_inputs_before_start(script, tmp_path):
    source = Path(__file__).parents[1] / 'fixtures' / 'real-trial'
    trial = tmp_path / 'trial'
    trial.mkdir()
    shutil.copy2(source / script, trial / script)
    command = ['bash', str(trial / script)] if script.endswith('.sh') else [sys.executable, str(trial / script)]
    result = subprocess.run(command, cwd=tmp_path, env=dict(os.environ, REFS_TRIAL_ISOLATED='1'), capture_output=True, text=True)
    assert result.returncode == 2
    assert result.stdout == ''
    assert len(result.stderr.splitlines()) == 1
    assert 'papers/pipyer-paper/references.bib' in result.stderr
    assert 'inputs/attention.json' in result.stderr
    assert "the owner's files kept out of the repository" in result.stderr
    assert not (trial / 'out').exists()
