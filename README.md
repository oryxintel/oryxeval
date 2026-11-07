# oryxeval

**Cheap, durable LLM evals. Free, local, and you never pay twice for the same answer.**

Every arm of an eval matrix (prompt x model x ...) is a cached cell, so a re-run pays only for what
changed. You get a confidence interval and a plain-English verdict on whether the change is
actually better. [pydantic-evals](https://pydantic.dev/docs/ai/evals/) does the scoring; oryxeval
adds the matrix, the cache, the intervals and the verdict. Built on
[oryxflow](https://github.com/oryxintel/oryxflow). Python 3.10+.

```
pip install oryxeval
```

## How it's different

- **Free, and it runs where your code runs.** A Python library: no platform, no account, no
  per-trace or per-score metering, no retention window. Your only bill is your model provider's,
  and the cache keeps that small. Results are files on your disk.
- **The cache is keyed on your code, not on the API request.** Most eval tools cache raw provider
  responses. oryxeval caches the whole arm: the function under test, the cases it read and the
  settings. So an agent that makes five model calls and a tool call per case is cached as one
  unit, an edited function re-runs on its own, and nothing expires after a couple of weeks.
- **Re-score for free.** Model outputs and scores are cached separately. Change a scorer or a
  judge rubric and only the scoring re-runs, over outputs you already paid for.
- **A verdict, not a dashboard.** Paired differences with intervals, a guardrail that must not
  get worse, a judge-vs-human agreement check, and a last line that says "inside noise" when it
  is.
- **It tests your production code as-is.** The thing under test is an ordinary async Python
  function that calls your real code. No YAML config, no rewriting it into a framework's
  pipeline format.

## The problem: prompt changes ship on vibes

- **Noise passes for a win.** The same prompt can score 69% and then 64% an hour later. Without an
  interval, a 5-point "improvement" is a coin flip you're about to ship.
- **The headline metric hides the regression.** A prompt that answers *everything* scores 100% on
  "did it answer", and also makes things up. A prompt that stays silent on hard cases looks great
  on quality.
- **Nobody checked the judge.** An LLM judge with no human labels behind it is an opinion with a
  percentage printed next to it.
- **Every re-run re-bills everything.** Tweak one prompt, or fix a typo in a judge rubric, and a
  hand-rolled script calls the model for every case and every arm again. So people run fewer
  evals, on fewer cases, and trust them less.
- **Stale results look fresh.** A hand-rolled cache keyed on the wrong thing quietly serves
  last week's outputs for this week's prompt.

## What else you get

- **Guardrails and coverage built in.** Name the metric that must not get worse (with a budget) and
  a winner that breaks it is reported as *not a clean win*. A quality rate on a filtered subset is
  shown next to how much it covers.
- **A bill before you spend.** Every run prints the projected call count (and cost, if you give
  it a per-call price) and asks first. One keystroke spends a single call to check credentials
  before committing to the rest.
- **Baselines from git.** Compare your working tree against the prompt as it was at any commit,
  without copying files around.
- **Where to look next.** Slice the best arm by any metadata column, worst first, and write a
  side-by-side of every case where the arms disagree, straight from the stored outputs.

## Quick example

Write the async function you want to compare. Any keyword holding a list is an axis: two prompt
versions make two arms.

```python
import oryxeval as ev
from pydantic import BaseModel


class Turn(BaseModel):
    question: str
    phrasing: str = 'plain'


async def run_turn(inputs, prompt_version):
    return await my_assistant(inputs.question, prompt=prompt_version)   # your code


r = ev.sweep(run_turn,
             cases=ev.load_cases('cases.csv', inputs=Turn),
             prompt_version=['prod', 'preship'],
             repeats=3,
             metric=ev.Metric('accuracy', 'correct'),
             guardrail=ev.Metric('false positives', 'false_positive',
                                 higher_is_better=False, budget=0.05),
             slices=('phrasing',))
r.verdict()
```

Before anything is billed:

```text
run_turn · 20 cases × 2 arms × 3 reps = 120 calls
  cached 0 · new 120   (+1 preflight call per new arm)

Run 120 new calls for run_turn? (y/n/c=check one call first)
```

Then the verdict, with intervals. Run it again and it costs nothing:

```text
run_turn · 20 cases × 2 arms × 3 reps = 120 calls
  cached 120 · new 0
```

## Let your coding agent run it

The [oryxeval Claude Code plugin](https://github.com/oryxintel/oryxeval-claude-plugin) takes an
agent from "I changed this prompt" to a verdict in four commands: plan the eval from your diff,
scaffold it, harvest real cases from the repo, and run it. It always shows the bill and waits
before spending.

## Docs

- [LLM evals quickstart](https://docs.oryxflow.dev/docs/llm-evals-quickstart/): a complete eval
  in one file, with what each line does and what it prints.
- [The guide](https://docs.oryxflow.dev/docs/llm-evals/): guardrails, judges, baselines, slices
  and the method behind the verdict.

## Coming from `oryxflow.evals`

oryxeval was split out of `oryxflow.evals`. To keep an existing eval's cache, change only its
import lines and no function body: the steps are in [CHANGELOG.md](CHANGELOG.md) (`26.11.6`).

## License

MIT
