# Publishing a release to PyPI

Maintainer-facing. Same pipeline as oryxflow (its `devops/publish.md` has the full background):
GitHub Actions builds and uploads, using **PyPI Trusted Publishing** (OIDC). There is no API token
anywhere, and every file gets a PEP 740 attestation.

## quickstart

```bash
git push github main
git tag v26.11.6 && git push github v26.11.6
gh release create v26.11.6 --generate-notes   # run ONCE; this is what uploads to PyPI
gh run watch                                  # the Release run; done when publish is green
```

## Release checklist

1. **oryxflow first.** If this release needs a newer oryxflow (`dependencies` in
   `pyproject.toml`), that oryxflow must already be on PyPI, or the tests workflow and every
   `pip install oryxeval` fail.
2. **Bump the version** in `pyproject.toml` (`version =`). Calver, `YY.M.D`, the same version
   as the oryxflow release it ships with when they go out together.
3. **Update `CHANGELOG.md`**: move `## [Unreleased]` bullets into a dated
   `## [26.11.6] - 2026-11-06` section.
4. **Commit, push, wait for the Tests workflow to go green.**
5. **Tag and publish a GitHub Release** (quickstart above). Publishing the release is the only
   confirmation step: there is no reviewer approval.
6. **Verify** (below). PyPI never allows re-uploading a version: if something is wrong, yank it
   and release the next version.

## One-time setup

**On PyPI**: before the first release the project does not exist, so add a *pending* publisher
(Account → Publishing → Add a new pending publisher); afterwards it lives under project `oryxeval`
→ Manage → Publishing.

| Field | Value |
| --- | --- |
| PyPI project name | `oryxeval` |
| Owner | `oryxintel` |
| Repository | `oryxeval` |
| Workflow filename | `release.yml` |
| Environment | `pypi` |

**On GitHub**: Settings → Environments → an environment named exactly `pypi`, with one
protection rule: *Deployment branches and tags* → *Selected branches and tags* → a **Tag** rule
`v*` (a *Branch* rule `v*` rejects every release). **No required reviewers**: an unapproved run
waits silently and GitHub cancels it after 30 days.

`release.yml` must be on `main`: the `release: published` trigger runs the workflow from the
default branch.

## Verifying a release

- The Release run's *publish* job is green.
- `pip download oryxeval==26.11.6 --no-deps` fetches the wheel. (PyPI's JSON API can lag a few
  minutes behind the file index.)
- The file's detail page on PyPI shows a **Trusted Publisher** provenance chip.

## Troubleshooting

| Symptom | Cause |
| --- | --- |
| Publish fails: "The deployment was rejected or didn't satisfy other protection rules" | The tag does not match the `pypi` environment's tag rule, or its rules changed while the run waited. Fix the rule, then `gh run rerun <run-id> --failed` (the build artifact is kept). |
| Job stuck on "Waiting for approval" | A required reviewer was added to `pypi`. Remove it, then re-run the failed run. |
| `gh release create`: `Release.tag_name already exists` | The release exists from an earlier attempt. Don't create another; re-run the failed run. |
| Publish fails at the OIDC exchange | Publisher not registered on PyPI, or a field mismatch (owner, repo, workflow filename, environment). |
| Workflow never runs | The release was saved as a draft, or `release.yml` is not on `main`. |
| `File already exists` | That version is already on PyPI. Bump and re-release. |
