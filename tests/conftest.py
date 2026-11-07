import os
import sys

# Typer forces colour on GitHub Actions (GITHUB_ACTIONS / FORCE_COLOR / PY_COLORS), which splits
# flag names in help text into styled runs, so help assertions failed on CI only. Plain help for
# the tests: flags, parsing and errors are unchanged; only the Rich styling is skipped. Typer reads
# this once, at import, so it must be set before anything imports typer.
os.environ['TYPER_USE_RICH'] = '0'

import pytest

@pytest.fixture(autouse=True)
def _no_oryxflow_evals():
    # an installed pre-split oryxflow still ships oryxflow.evals; importing it loads a second TaskEval
    yield
    assert 'oryxflow.evals' not in sys.modules, 'a test or module imported oryxflow.evals; use oryxeval'
