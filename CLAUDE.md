# CLAUDE.md

Guidance for working in the **oryxeval** repo.

## Role and autonomy

Work as a senior software / data engineer. Prioritize by real user pain from eval users'
feedback notes (tracked outside this repo): silent wrong results and stale or re-billed caches
first, then recurring friction, then polish. Fix root causes with tests; keep the public API
small and CHANGELOG, docs and the plugin skill in sync. Work mostly autonomously, but surface
every major decision the user might want to weigh in on or reverse (API design and naming, new
semantics, breaking changes, deferring a reported issue) in a "Decisions" list in your report,
and stop to ask before releases, pushes or anything irreversible.

## What this is

`oryxeval` (`import oryxeval as ev`) is the LLM-eval harness split out of oryxflow
(`oryxflow.evals` up to oryxflow 26.10.22). It builds on oryxflow: every arm of an eval matrix is
a cached oryxflow task; pydantic-evals does the scoring. It has no console script: the CLI is
`ev.cli(MyEval)` called from the user's own `run_eval_<name>.py`.

## Layout

```
oryxeval/
  __init__.py   # public API + re-exports of oryxflow's Parameter types and hash_files
  baseline.py   # git_tree / git_sha / Variant / PromptArm; the _oryxflow_baseline.json manifest
  cases.py      # load_cases, CaseList, RESERVED_METADATA
  cli.py        # ev.cli / build_app (Typer flags derived from the task's Parameters)
  metric.py     # Metric
  sidebyside.py # EvalResult.side_by_side rendering (Jinja)
  stats.py      # rate_ci, delta_ci, judge_alignment, corrected_rate
  sweep.py      # sweep(), EvalResult
  task.py       # TaskEval, EvalOutputs, EvalFailureRateError
tests/          # pytest; metric/verdict tests run on hand-built DataFrames
docs/todo/      # design notes (plans)
CHANGELOG.md  README.md
.githooks/     # pre-commit: changelog lint + check_private_terms.py
.github/workflows/  # tests.yml (matrix), release.yml (PyPI Trusted Publishing)
```

## SEAM

The per-case DataFrame is the interface. Everything downstream of a run (`Metric`, slices,
intervals, verdict, report) reads only that frame and never touches a pydantic-evals object. The
two override points on `TaskEval` are the exit: `_evaluate()` returns a report (swap the
runner), `_to_frame(report)` returns the rows (swap the report shape). Keep it that way: every
metric, verdict and report test is written against a hand-built DataFrame.

## oryxflow symbols we depend on

The dependency runs one way, oryxeval -> oryxflow. Keep this table current; oryxflow's
`tests/test_oryxeval_contract.py` guards the private ones.

| oryxeval module | oryxflow symbol it uses |
| --- | --- |
| `__init__.py` | re-exports oryxflow's nine `Parameter` classes and `hash_files` (the same objects) |
| `task.py` | `oryxflow.tasks.TaskJson` (base of `EvalOutputs`), `oryxflow.tasks.TaskPqPandas` (base of `TaskEval`), `oryxflow.IntParameter`, `oryxflow.codehash.task_code_hash`, `oryxflow.codehash.callable_code_hash`, `oryxflow.codehash.strip_docstrings` |
| `sweep.py` | `oryxflow.WorkflowMulti`, `oryxflow.runIterConcat`, `oryxflow.hash_files`, `oryxflow.codehash.callable_code_hash`, `Parameter` / `Int` / `Float` / `Bool` / `List` / `DictParameter` |
| `cli.py` | `oryxflow.parameter.{Bool,Choice,Date,Dict,Enum,Float,Int,List}Parameter` |
| `baseline.py` | `oryxflow.utils.hash_files` |
| tests | `oryxflow.settings.{dir,dirpath,eventspath}`, `oryxflow.state.clear_cache()`, `oryxflow.core._code_warned` (private) |

## Cache identity is frozen

Existing eval caches must stay valid, so:

- **A module path must never enter a cache key.** `task_id` is class name + params hash; the arm
  identity is `_source_hash(target)` + `callable_code_hash(case callables)` + `_case_digest` +
  `OUTPUTS_VERSION`; the scoring identity is per-evaluator `{class, code, spec}` + `FRAME_VERSION`.
  Generated classes take the user's `__module__`.
- `_source_hash` must stay byte-identical (it uses `oryxflow.codehash.strip_docstrings`).
- Do not rename the baseline manifest `_oryxflow_baseline.json` or oryxflow's `.oryxflow/` events
  dir.

## Running tests

Use the machine `python`, which has oryxflow installed from a sibling `../oryxflow` checkout
(check `python -c "import oryxflow; print(oryxflow.__file__)"`). Run tests from the repo root:

```
PYTHONPATH=. python -m pytest tests -q -p no:cacheprovider
```

Never `pip install -e`, and never create a venv, `build/` or `dist/` in this folder (it is
cloud-synced). Build wheels from a clone in a scratch directory outside the workspace.

## Plans (design notes you can execute from a clean session)

Non-trivial work is planned first and saved in the repo at `docs/todo/<YYYYMMDD>-<area>-<topic>.md`
(`<area>` is a short tag such as `evals`, `sys`). The workflow: write the plan, clear the
session, then say "execute `docs/todo/<file>.md`". The new session has no memory of the
planning conversation, so the plan must be self-contained.

A plan file MUST contain, in order:

1. **`## Context`** - the WHY: the problem, what prompted it, the intended outcome, the current
   limiting behavior (quote real output where it helps).
2. **`### Design decisions`** - the choices and why, notably what was rejected. Mark anything the
   user confirmed.
3. **`## Implementation`** - numbered steps, each naming the exact file and function/seam, with
   the code or precise change.
4. **`## Files modified`** - one line per file.
5. **`## Verification`** - commands, expected output, and the test baseline to hold.

Don't reference "the conversation". When implemented, leave the file in `docs/todo/`, append
`## Implementation notes (divergences from the plan as built)` if the build diverged, and commit
the plan in the same commit as the code.

## Never write private identifiers into repo files

**This repo is public and git history is forever.** Applies to every committed file: docs, code,
comments, commit messages, and especially `docs/todo/` plans. Sanitize as you write, not later.

| Don't | Do |
| --- | --- |
| Absolute local paths | A repo-relative path, or the repo name |
| An out-of-repo file's location | "tracked in an external note, `<filename>.md`" |
| Client / customer / employer names, incl. as a directory or project slug | "a downstream consumer project" |
| A client's data vendors, systems, or class names that embed them | A generic stand-in |
| Other private project codenames | "a private sibling project", or omit |
| Credential-shaped strings: tokens, keys, bucket names, internal hostnames/URLs | A placeholder (`<PYPI_TOKEN>`), or say where it is stored |

A plan must stay executable after sanitizing: keep the shape of the real example, drop only the
identity.

`.githooks/pre-commit` blocks a commit that adds a local path or a listed client name (from
`~/.oryx-private-terms` or a gitignored `.private-terms`), or a `BREAKING:` changelog bullet
without `Migration:`. Enable it once per clone: `git config core.hooksPath .githooks`.

## Conventions

- Version is calver; provisional `26.11.0` until the maintainer stamps a release. Unreleased work
  goes under `## [Unreleased]` in `CHANGELOG.md`; every breaking change starts with `BREAKING:` and
  carries a `Migration:` clause.
- Commits: imperative summary line; end with the Co-Authored-By trailer.
- Platform is Windows; tests compare against `pathlib.Path(...)` so they pass cross-OS.
- User docs are written for data scientists: say what the reader gets and what to type, not how it
  is computed.
