import sys
import pytest

@pytest.fixture(autouse=True)
def _no_oryxflow_evals():
    # an installed pre-split oryxflow still ships oryxflow.evals; importing it loads a second TaskEval
    yield
    assert 'oryxflow.evals' not in sys.modules, 'a test or module imported oryxflow.evals; use oryxeval'
