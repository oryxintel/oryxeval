"""Pins _source_hash, which keys every eval's model-call stage.

Changing its output moves EVERY existing cache key, so every user re-pays for every model call.
Don't update the value to make the test pass; keep the old output. ast.dump's format is per
Python minor, hence one value per version.
"""
import sys

import pytest

from oryxeval.task import _source_hash


def _golden_fn(x):
    """Doc."""
    return x + 1


GOLDEN = {(3, 12): '56a42e183869d1be'}


@pytest.mark.skipif(sys.version_info[:2] not in GOLDEN, reason='no golden for this Python')
def test_source_hash_golden():
    assert _source_hash(_golden_fn) == GOLDEN[sys.version_info[:2]]
