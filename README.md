# oryxeval

Cheap, durable LLM evals. Every arm of an eval matrix (prompt x model x ...) is a cached cell, so
a re-run pays only for what changed. pydantic-evals does the scoring; oryxeval adds the matrix,
the cache, intervals and a verdict. Built on [oryxflow](https://github.com/oryxintel/oryxflow).

Python 3.10+.

```
pip install oryxeval
```

## The six-line quick eval

Write the async function you want to compare and hand it to `ev.sweep`. A keyword holding a
list is an axis (two prompt versions = two arms):

```python
import oryxeval as ev
from pydantic import BaseModel


class Turn(BaseModel):
    question: str
    phrasing: str = 'plain'


async def run_turn(inputs, prompt_version):
    return await my_assistant(inputs.question, prompt=prompt_version)   # your code
```

```python
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

Docs: [LLM evals quickstart](https://docs.oryxflow.dev/docs/llm-evals-quickstart/) and the [guide](https://docs.oryxflow.dev/docs/llm-evals/).

Moved from `oryxflow.evals`. To keep an existing eval's cache, change only its import lines and
no function body: the steps are in [CHANGELOG.md](CHANGELOG.md) (`[Unreleased]`).
