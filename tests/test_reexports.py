import pathlib, re

def test_reexports_are_oryxflow_objects():
    import oryxflow, oryxeval
    for n in ['Parameter', 'IntParameter', 'FloatParameter', 'BoolParameter', 'ChoiceParameter',
              'ListParameter', 'DictParameter', 'DateParameter', 'EnumParameter', 'hash_files']:
        assert getattr(oryxeval, n) is getattr(oryxflow, n)
        assert n in oryxeval.__all__

def test_version():
    import oryxeval
    assert isinstance(oryxeval.__version__, str)

def test_pyyaml_declared():  # regex, not tomllib: oryxeval supports 3.10
    deps = re.search(r'dependencies\s*=\s*\[([^\]]*)\]',
                     (pathlib.Path(__file__).parents[1] / 'pyproject.toml').read_text()).group(1)
    assert re.search(r'["\']pyyaml', deps, re.I)

def test_source_hash_uses_public_strip():
    import inspect, oryxeval.task
    src = inspect.getsource(oryxeval.task)
    assert 'strip_docstrings' in src and '_strip_docstrings' not in src
