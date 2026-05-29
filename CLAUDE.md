# 🚀 Releases

This repo uses **date-based git tags** + **`CHANGELOG.md`** keyed by date as the release record. `CHANGELOG.md` is the source of truth for what landed when. GitHub Releases is optional — use it when you want a permalinkable page with attached assets (e.g., for a blog post linking the first published baseline).

Day-on-day progress lives in commit history. Tagged releases mark checkpoints worth pointing at (first working `load_wesad`, first baseline accuracy number, first published blog artifact, etc.).

## Tag naming

`YYYY-MM-DD` — matches commit dates and reads as a chronological log without implying a semver contract that doesn't apply to a research repo. No `v` prefix. Same-day collisions get a numeric suffix: `YYYY-MM-DD-2`, `YYYY-MM-DD-3`.

## CHANGELOG entries

`CHANGELOG.md` lives at the repo root. Each release gets a `## YYYY-MM-DD` section matching its tag.

Within an entry, the convention is **human-written, narrative, and brief** — a curated highlight reel of what mattered, not a Keep-a-Changelog `Added/Changed/Fixed` bucket list, not an exhaustive auto-bulleted diff of every file touched. Themed H3 sub-sections (e.g., `### Middleware`, `### MLflow UI`), short paragraphs, surprises and gotchas captured explicitly, screenshots and links inline where they help.

AI assistants should not auto-fill CHANGELOG entries from `git log` or diffs. When asked to update the CHANGELOG, either ask the project owner what they want captured, or draft a short narrative entry from the most surprising / load-bearing changes — and expect a rewrite. The commit history is the full audit trail; the CHANGELOG is the FYI-for-future-readers layer on top of that.

Use past entries (e.g., `2026-05-27`) as the style reference.

## Images

Screenshots, plots, and other binary assets go in `images/` at the repo root. Naming: `YYYY-MM-DD-<short-topic>.png` (or `.jpg`, `.svg`). Reference them from CHANGELOG entries with a relative markdown link:

```markdown
![smoke test](./images/2026-05-27-mlflow-smoke-test.png)
```

## Cutting a release

With `CHANGELOG.md` already updated and committed, from the repo root:

```bash
git tag -a "$(date +%Y-%m-%d)" -m "<one-line release message>"
git push origin "$(date +%Y-%m-%d)"
```

For same-day collisions, hand-suffix `-2` / `-3` in place of `$(date +%Y-%m-%d)`. The push needs network access and credentials for the git remote, so it should be run from a workstation with those configured — not from a sandboxed assistant environment.

# 📐 Artifact discipline

The repo is a public research artifact. Notebooks, READMEs, schema docs, CHANGELOG entries, and commit messages should read as clean work to a stranger landing from a blog post or GitHub search — not as personal scaffolding.

## What stays out

- **Personal todos and execution-flow markers** — phrases like `Stop here today`, `Next: …`, `do this tomorrow`, `first function to write tomorrow`, or `TODO`/`FIXME` in prose. A notebook's closing markdown should describe what was demonstrated (backward-looking), not what to do next (forward-looking).
- **Internal codenames or workstream labels** — anything that requires context outside the repo to parse. Use neutral phrasing instead: "the baseline pipeline" not internal project labels, "the first published baseline" not a tracking code.
- **Day-of-week labels as sequencing** — `Thu work`, `Fri/Mon follow-up`, etc. Days don't carry meaning to a reader without your calendar. Phrase by deliverable or absolute date.
- **Hardcoded user paths** — `/Users/<name>/...` in any code block or README snippet. Assume the reader is at the repo root or use a placeholder like `<repo>`.

## Prose matches code

Markdown around code must describe what the code mechanically does, not what it aspires to. If a claim ("verified by X, not by trusting Y") is stronger than what the code delivers (which only compares X and Y side-by-side), soften the prose. Aspirational methodological discipline in docs that the code doesn't actually enforce is documentation drift and erodes trust on the second read.

## Before commit

Grep the staged set for both leak classes — internal-context leaks and personal-todo leaks — before pushing:

```bash
git diff --cached --name-only | xargs grep -nE 'today\.md|calibration-log|/Users/|TODO|FIXME'
git diff --cached --name-only | xargs grep -nE 'Stop here|tomorrow|yesterday|first function to write|Next:'
```

Both should return empty. If either matches, fix before committing — these are cheap to catch with grep and awkward to find after push.
