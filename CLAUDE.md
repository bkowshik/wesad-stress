# 🚀 Releases

This repo uses **date-based git tags** + **`CHANGELOG.md`** keyed by date as the release record. `CHANGELOG.md` is the source of truth for what landed when. GitHub Releases is optional — use it when you want a permalinkable page with attached assets (e.g., for a blog post linking the Scout 1 baseline).

Day-on-day progress lives in commit history. Tagged releases mark checkpoints worth pointing at (first working `load_wesad`, first baseline accuracy number, Scout 1 blog artifact, etc.).

## Tag naming

`YYYY-MM-DD` — matches the vault's journal and `todos/days/` naming, so the tag and the journal entry share an index key. No `v` prefix (reads as semver, which doesn't apply to a research repo). Same-day collisions get a numeric suffix: `YYYY-MM-DD-2`, `YYYY-MM-DD-3`, mirroring the vault rule for journal/note filename collisions.

## CHANGELOG entries

`CHANGELOG.md` lives at the repo root. Each release gets a `## YYYY-MM-DD` section matching its tag.

Within an entry, the convention is **human-written, narrative, and brief** — Bhargav's curated highlight reel of what mattered, not a Keep-a-Changelog `Added/Changed/Fixed` bucket list, not an exhaustive auto-bulleted diff of every file touched. Themed H3 sub-sections (e.g., `### Middleware`, `### MLflow UI`), short paragraphs in his voice, surprises and gotchas captured explicitly, screenshots and links inline where they help.

Claude does not auto-fill CHANGELOG entries from `git log` or diffs. When asked to update CHANGELOG, either ask Bhargav what he wants captured, or draft a short narrative entry from the most surprising / load-bearing changes — and expect him to rewrite it. The commit history is the full audit trail; the CHANGELOG is the FYI-for-future-me layer on top of that.

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

For same-day collisions, hand-suffix `-2` / `-3` in place of `$(date +%Y-%m-%d)`. The push runs over the user's existing git remote — meant to be run from the host machine, not from a Cowork sandbox (which has no SSH credentials for GitHub).
