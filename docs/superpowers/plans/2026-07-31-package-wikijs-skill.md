# Package wikijs skill as standalone plugin — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the personal `wikijs` Claude Code skill into a standalone, installable plugin (`claude-wikijs-skill`), generalized for any Wiki.js 2.x user, with a real fix for the missing tag-update capability.

**Architecture:** Single-repo Claude Code plugin that is also its own dev/distribution marketplace (`.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` with `source: "./"`). The CLI script (`skills/wikijs/scripts/wikijs.py`) is copied over unchanged except for one fix (a new pure `resolve_tags()` function wired into `update --tags`). `SKILL.md` is generalized (plugin-root paths, explicit Wiki.js-2.x-only and Markdown-only callouts) and the personal journaling convention is extracted into a separate example doc.

**Tech Stack:** Python 3 (`requests`), pytest (one small unit test for the new tag-resolution logic), Claude Code plugin manifest format (JSON).

**Spec:** `docs/superpowers/specs/2026-07-31-package-wikijs-skill-design.md`

---

## File Structure

```
claude-wikijs-skill/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   └── wikijs/
│       ├── SKILL.md
│       └── scripts/
│           └── wikijs.py
├── tests/
│   └── test_wikijs.py
├── docs/
│   ├── journal-convention-example.md
│   └── superpowers/
│       ├── specs/2026-07-31-package-wikijs-skill-design.md   (already committed)
│       └── plans/2026-07-31-package-wikijs-skill.md            (this file)
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── README.md
├── LICENSE
└── CHANGELOG.md
```

Each file's job:
- `wikijs.py` — the CLI, unchanged from the personal copy except the tag fix.
- `SKILL.md` — what Claude reads to know how to use the CLI; generic, no personal convention.
- `journal-convention-example.md` — the extracted personal convention, framed as an optional example.
- `plugin.json` / `marketplace.json` — Claude Code plugin manifests.
- `README.md` — human-facing install/setup docs.
- `tests/test_wikijs.py` — narrow unit test for the new `resolve_tags()` function only (the broader CLI test suite is deferred per spec's Future Work section).

---

### Task 1: Repo scaffold (license, gitignore, changelog stub, dirs)

**Files:**
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `CHANGELOG.md`

- [ ] **Step 1: Create `.gitignore`**

```
__pycache__/
*.pyc
.venv/
venv/
.env
.DS_Store
```

- [ ] **Step 2: Create `LICENSE`** (MIT)

```
MIT License

Copyright (c) 2026 Michael Paulukonis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Create `CHANGELOG.md`**

```markdown
# Changelog

## 0.1.0 - 2026-07-31

- Initial extraction from personal dot-files skill collection.
- Generalized install paths for Claude Code plugin use (`${CLAUDE_PLUGIN_ROOT}`).
- Added `update --tags` to set/clear page tags (previously `update` silently
  preserved existing tags only, with no way to change them).
- Documented Wiki.js 2.x-only and Markdown-only limitations explicitly.
```

- [ ] **Step 4: Verify and commit**

Run: `git status`
Expected: three new untracked files listed (`.gitignore`, `LICENSE`, `CHANGELOG.md`)

```bash
git add .gitignore LICENSE CHANGELOG.md
git commit -m "Scaffold repo: license, gitignore, changelog"
```

---

### Task 2: Copy `wikijs.py` unmodified, add Python dependency files

**Files:**
- Create: `skills/wikijs/scripts/wikijs.py` (copied from dot-files)
- Create: `requirements.txt`
- Create: `.env.example`

- [ ] **Step 1: Create directories and copy the script verbatim**

```bash
mkdir -p skills/wikijs/scripts
cp /Users/michaelpaulukonis/projects/dot-files/claude/skills/wikijs/scripts/wikijs.py \
   skills/wikijs/scripts/wikijs.py
```

- [ ] **Step 2: Verify the copy is intact and runnable**

Run: `python3 skills/wikijs/scripts/wikijs.py --help`
Expected: argparse usage output listing subcommands (`create`, `update`, `get`,
`search`, `list`, `delete`, `move`, `upload`, `folders`, `assets`,
`delete-asset`, `rename-asset`) — script exits 0, no `WIKIJS_TOKEN` error yet
because `--help` short-circuits before the token check in some argparse setups;
if you instead see `error: WIKIJS_TOKEN not set...`, that's also fine — it
means the copy is intact and executable, just confirming the token guard at
`main()` fires before argparse in this script's structure.

- [ ] **Step 3: Create `requirements.txt`**

```
requests>=2.28
```

- [ ] **Step 4: Create `.env.example`**

```
WIKIJS_API_URL=http://localhost
WIKIJS_TOKEN=
```

- [ ] **Step 5: Commit**

```bash
git add skills/wikijs/scripts/wikijs.py requirements.txt .env.example
git commit -m "Add wikijs.py CLI and Python dependency files"
```

---

### Task 3: TDD the `update --tags` fix

This is the one functional change from the personal version: `update` currently
fetches existing tags and passes them back unchanged (see the comment at
`skills/wikijs/scripts/wikijs.py:99-101` after the copy in Task 2) — there is no
way to add, remove, or replace tags. Fix: extract a pure `resolve_tags()`
function (independently testable, no network calls) and wire it into
`cmd_update` plus a new `--tags` CLI flag.

**Files:**
- Create: `requirements-dev.txt`
- Create: `tests/test_wikijs.py`
- Modify: `skills/wikijs/scripts/wikijs.py`

- [ ] **Step 1: Create `requirements-dev.txt`**

```
pytest>=7
```

- [ ] **Step 2: Install dev dependencies**

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

- [ ] **Step 3: Write the failing test**

Create `tests/test_wikijs.py`:

```python
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "skills" / "wikijs" / "scripts")
)

import wikijs  # noqa: E402


def test_resolve_tags_none_keeps_existing():
    assert wikijs.resolve_tags(None, ["a", "b"]) == ["a", "b"]


def test_resolve_tags_empty_string_clears():
    assert wikijs.resolve_tags("", ["a", "b"]) == []


def test_resolve_tags_parses_and_strips_whitespace():
    assert wikijs.resolve_tags("a, b ,c", []) == ["a", "b", "c"]
```

- [ ] **Step 4: Run test to verify it fails**

Run: `pytest tests/test_wikijs.py -v`
Expected: `AttributeError: module 'wikijs' has no attribute 'resolve_tags'` (or
similar collection error) — the function doesn't exist yet.

- [ ] **Step 5: Implement `resolve_tags()`**

In `skills/wikijs/scripts/wikijs.py`, add this function right after
`read_content_arg` (around line 69, before the `# ---------- commands ----------`
comment):

```python
def resolve_tags(tags_arg: str | None, existing_tags: list[str]) -> list[str]:
    """Return the tag list to send: parsed --tags value if given, else existing
    tags unchanged. Empty string clears all tags."""
    if tags_arg is None:
        return existing_tags
    return [t.strip() for t in tags_arg.split(",") if t.strip()]
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/test_wikijs.py -v`
Expected: `3 passed`

- [ ] **Step 7: Wire `resolve_tags()` into `cmd_update` and add the `--tags` flag**

In `skills/wikijs/scripts/wikijs.py`, modify `cmd_update` — replace:

```python
    page = data["pages"]["single"]
    if not page:
        die(f"page id {page_id} not found")
    tags = [t["tag"] for t in page.get("tags") or []]
```

with:

```python
    page = data["pages"]["single"]
    if not page:
        die(f"page id {page_id} not found")
    existing_tags = [t["tag"] for t in page.get("tags") or []]
    tags = resolve_tags(args.tags, existing_tags)
```

Then in `main()`, in the `update` subparser block, add the new flag — replace:

```python
    p = sub.add_parser("update", help="replace or append page content")
    p.add_argument("ref", help="page path or numeric id")
    p.add_argument("--replace")
    p.add_argument("--replace-file")
    p.add_argument("--append")
    p.add_argument("--append-file")
    p.set_defaults(func=cmd_update)
```

with:

```python
    p = sub.add_parser("update", help="replace or append page content")
    p.add_argument("ref", help="page path or numeric id")
    p.add_argument("--replace")
    p.add_argument("--replace-file")
    p.add_argument("--append")
    p.add_argument("--append-file")
    p.add_argument(
        "--tags",
        help="comma-separated; replaces all existing tags. "
             "Omit to leave tags unchanged; pass --tags \"\" to clear all tags.",
    )
    p.set_defaults(func=cmd_update)
```

- [ ] **Step 8: Manually verify the flag is wired (no live wiki needed)**

Run: `python3 skills/wikijs/scripts/wikijs.py update --help`
Expected: usage output includes the new `--tags` line with the help text above.

- [ ] **Step 9: Run full test suite once more**

Run: `pytest tests/ -v`
Expected: `3 passed`

- [ ] **Step 10: Commit**

```bash
git add requirements-dev.txt tests/test_wikijs.py skills/wikijs/scripts/wikijs.py
git commit -m "Add update --tags flag with TDD'd resolve_tags() helper"
```

---

### Task 4: Write generalized `SKILL.md`

**Files:**
- Create: `skills/wikijs/SKILL.md`

- [ ] **Step 1: Create `skills/wikijs/SKILL.md`**

```markdown
---
name: wikijs
description: Use when working with a personal Wiki.js 2.x instance - journaling, creating or editing wiki pages, uploading images or files to the wiki, or searching/reading wiki content ("what did I write about X").
---

# Wiki.js CLI

Thin wrapper for a Wiki.js **2.x** instance. All operations go through
`scripts/wikijs.py`. No MCP server needed.

> **Wiki.js 2.x only.** This wraps the 2.x GraphQL schema (`pages.singleByPath`,
> `assets.folders`, etc). Wiki.js 3.x is a different, still-beta schema and is
> not supported.

> **Markdown only.** Pages are created/updated with `editor: "markdown"`
> hardcoded. Wiki.js 2.x also offers HTML and CKEditor page editors, but this
> skill doesn't support them yet.

## Setup

One-time:

```bash
pip install -r ${CLAUDE_PLUGIN_ROOT}/requirements.txt
cp ${CLAUDE_PLUGIN_ROOT}/.env.example ~/.config/wikijs.env
# edit ~/.config/wikijs.env: set WIKIJS_API_URL and WIKIJS_TOKEN
# (generate WIKIJS_TOKEN from Wiki.js Admin -> Users -> API Access)
```

Every invocation needs env vars sourced first:

```bash
set -a; source ~/.config/wikijs.env; set +a
python3 ${CLAUDE_PLUGIN_ROOT}/skills/wikijs/scripts/wikijs.py <command> ...
```

Fails fast with a clear message if `WIKIJS_TOKEN` is missing or the wiki is down.

## Commands

```
create <path> <title> [--content S | --content-file F] [--tags a,b] [--description S]
update <path|id> [--append S | --append-file F | --replace S | --replace-file F] [--tags a,b]
get <path|id>          # content on stdout, metadata JSON on stderr
search <query>         # id, path, title per line
list [--limit N]       # most recently updated first
delete <path|id> --yes # refuses without --yes
move <path|id> <new-path>            # rename/move a page; changes its path
upload <file> [--folder <slug|id>]   # prints embed path, e.g. /test-verify/img.png
folders                # asset folders: id, slug, name
assets [--folder <slug|id>]          # assets in folder: id, filename, size, updated
delete-asset <id> --yes
rename-asset <id> <new-filename>     # filename only
```

`update --tags a,b,c` replaces the page's tags entirely; omit `--tags` to leave
tags unchanged; pass `--tags ""` to clear all tags.

## Journaling

This skill has no built-in journal convention. See `docs/journal-convention-example.md`
in this plugin for one worked example you can copy and adapt - path format,
title format, section structure, all of it is up to you.

## Upload → embed example

```bash
path=$(python3 ${CLAUDE_PLUGIN_ROOT}/skills/wikijs/scripts/wikijs.py upload diagram.png --folder journal)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/wikijs/scripts/wikijs.py update some/page \
  --append "![diagram]($path)"
```

Max upload 5 MB (server default); script pre-checks and errors readably.

## Quirks

- Search result ids can be stale - trust the `path` column, never the id.
- A failed `update` may still have written content (Wiki.js applies content
  before some validations). `get` to check state before retrying.
- No folder delete exists in the Wiki.js 2.x API - don't look for one.
  Asset folders can only be created (`folders` lists them).
- No asset move-between-folders or metadata edit either (verified by schema
  introspection: only createFolder, renameAsset, deleteAsset, flushTempUploads).
  To "move" an asset: download it, `upload` to the target folder, `delete-asset`
  the original, update any pages embedding the old path.
- Pages, unlike assets, have a native move: `move` calls the `pages.move`
  mutation directly - no download/reupload/delete dance needed.
- Never upload assets with `.md`, `.html`, or `.txt` extensions - the router
  treats those as page paths, so the asset 404s even though the upload succeeds.
  Rename before upload (`.markdown` works); `rename-asset` refuses extension
  changes after the fact.
- Page create/update rejects empty or whitespace-only content ("Page content
  cannot be empty"). For an intentionally blank page use `--content "<!-- -->"`.
- The API token is full admin. Delete is guarded by `--yes`; keep it that way.
```

- [ ] **Step 2: Commit**

```bash
git add skills/wikijs/SKILL.md
git commit -m "Add generalized SKILL.md"
```

---

### Task 5: Extract journal convention example doc

**Files:**
- Create: `docs/journal-convention-example.md`

- [ ] **Step 1: Create `docs/journal-convention-example.md`**

```markdown
# Example: daily journal convention

This is one convention for journaling with the wikijs skill - adapt paths,
titles, and section structure to your own wiki. Nothing here is enforced by
`wikijs.py`.

- Entry path: `journal/{year}/{month}/{day}-{weekday}` - month/day zero-padded,
  weekday lowercase full name. Example: `journal/2026/07/18-saturday`
- Entry title: `{day} {Weekday}` - e.g. `18 Saturday`
- Entry body starts empty; append plain lines under the title, promote anything
  longer than a couple of lines to its own `## Section`
- Parent pages: `journal` has `## Years`, `journal/{year}` has `## Months`,
  `journal/{year}/{month}` has `## Entries` with day links sorted by day
- Journaling flow: `get` today's page; if missing, `create` it (and any missing
  parents top-down, adding the link to each parent's list section); then
  `update --append`
- When linking a wiki page in a response, prefix with your wiki's base URL
  (e.g. `http://localhost/`) rather than a bare path - bare paths aren't
  clickable in most chat UIs.
```

- [ ] **Step 2: Commit**

```bash
git add docs/journal-convention-example.md
git commit -m "Add journal convention as an optional example doc"
```

---

### Task 6: Plugin manifests

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Create `.claude-plugin/plugin.json`**

```json
{
  "name": "claude-wikijs-skill",
  "version": "0.1.0",
  "description": "Claude Code skill: CLI wrapper for a Wiki.js 2.x instance (pages, search, assets)",
  "author": { "name": "Michael Paulukonis" },
  "license": "MIT"
}
```

- [ ] **Step 2: Create `.claude-plugin/marketplace.json`**

```json
{
  "name": "claude-wikijs-skill",
  "description": "Development/distribution marketplace for the wikijs skill",
  "owner": { "name": "Michael Paulukonis" },
  "plugins": [
    {
      "name": "claude-wikijs-skill",
      "description": "CLI wrapper for a Wiki.js 2.x instance",
      "version": "0.1.0",
      "source": "./"
    }
  ]
}
```

- [ ] **Step 3: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); json.load(open('.claude-plugin/marketplace.json')); print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "Add Claude Code plugin and marketplace manifests"
```

---

### Task 7: Write `README.md`

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md`**

```markdown
# claude-wikijs-skill

Claude Code skill: a thin CLI wrapper for a Wiki.js **2.x** instance (pages,
search, assets). No MCP server - just a Python script Claude shells out to,
which keeps token overhead low for simple CRUD operations.

## Requirements

- A running Wiki.js **2.x** instance (not 3.x - different, still-beta schema)
- An admin API token (Wiki.js Admin -> Users -> API Access)
- Python 3.10+
- `requests` (see Setup)

## Install

As a Claude Code plugin:

```
/plugin marketplace add <owner>/claude-wikijs-skill
/plugin install claude-wikijs-skill@claude-wikijs-skill
```

Or manually: clone this repo and symlink/copy it into `~/.claude/skills/wikijs`.

## Setup

```bash
pip install -r requirements.txt
cp .env.example ~/.config/wikijs.env
# edit ~/.config/wikijs.env: set WIKIJS_API_URL and WIKIJS_TOKEN
```

## Usage

See `skills/wikijs/SKILL.md` for the full command reference. Once the plugin
is installed, Claude Code loads the skill automatically - ask it to search,
journal, or edit wiki pages and it uses the CLI under the hood.

For a worked example of a page-naming convention (journaling), see
`docs/journal-convention-example.md`.

## Limitations

- Wiki.js 2.x only.
- Markdown-edited pages only (Wiki.js's HTML/CKEditor editors aren't supported).
- No automated end-to-end test suite yet - see `docs/superpowers/specs/` for
  the current design doc and planned follow-up work.

## License

MIT - see `LICENSE`.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "Add README"
```

---

### Task 8: Manual smoke test against a real Wiki.js 2.x instance

No automated integration suite exists yet (deferred per spec). Exercise the
full command surface manually against your real instance, using a disposable
page path so nothing real gets clobbered.

**Files:** none (verification only)

- [ ] **Step 1: Source env and confirm connectivity**

```bash
set -a; source ~/.config/wikijs.env; set +a
python3 skills/wikijs/scripts/wikijs.py list --limit 3
```

Expected: three tab-separated rows (`id`, `/path`, `title`, `updatedAt`) from
your real wiki - confirms auth and connectivity.

- [ ] **Step 2: Create a disposable test page**

```bash
python3 skills/wikijs/scripts/wikijs.py create packaging-smoke-test "Packaging Smoke Test" \
  --content "initial content" --tags draft,smoke
```

Expected: `created id=<N> path=/packaging-smoke-test`

- [ ] **Step 3: Verify tags landed, then change them with `update --tags`**

```bash
python3 skills/wikijs/scripts/wikijs.py get packaging-smoke-test
```

Expected: stderr JSON metadata shows `"tags": ["draft", "smoke"]`.

```bash
python3 skills/wikijs/scripts/wikijs.py update packaging-smoke-test --tags verified
```

Expected: `updated id=<N>`

```bash
python3 skills/wikijs/scripts/wikijs.py get packaging-smoke-test
```

Expected: `"tags": ["verified"]` - confirms the fix from Task 3 works against a
live wiki, not just the unit test.

- [ ] **Step 4: Clear tags entirely**

```bash
python3 skills/wikijs/scripts/wikijs.py update packaging-smoke-test --tags ""
python3 skills/wikijs/scripts/wikijs.py get packaging-smoke-test
```

Expected: `"tags": []`

- [ ] **Step 5: Append content, search, move**

```bash
python3 skills/wikijs/scripts/wikijs.py update packaging-smoke-test --append "appended line"
python3 skills/wikijs/scripts/wikijs.py search "packaging-smoke"
python3 skills/wikijs/scripts/wikijs.py move packaging-smoke-test packaging-smoke-test-moved
```

Expected: `update` succeeds; `search` finds the page by title/content; `move`
prints `moved id=<N> -> /packaging-smoke-test-moved`.

- [ ] **Step 6: Upload an asset and embed it**

```bash
echo "test" > /tmp/smoke-test.txt
mv /tmp/smoke-test.txt /tmp/smoke-test.markdown  # avoid the .md/.txt upload trap
python3 skills/wikijs/scripts/wikijs.py upload /tmp/smoke-test.markdown
```

Expected: prints an embed path like `/smoke-test.markdown`.

```bash
python3 skills/wikijs/scripts/wikijs.py assets
```

Expected: the uploaded asset appears in the listing (note its `id`).

- [ ] **Step 7: Clean up — delete asset and page**

```bash
python3 skills/wikijs/scripts/wikijs.py delete-asset <asset-id-from-step-6> --yes
python3 skills/wikijs/scripts/wikijs.py delete packaging-smoke-test-moved --yes
rm /tmp/smoke-test.markdown
```

Expected: `deleted asset id=<N>` and `deleted id=<N>`.

- [ ] **Step 8: Note the result**

No commit for this task (verification only) — if any step failed, fix the
underlying issue in `wikijs.py` or `SKILL.md` before moving on, re-running
Task 8 from the top.

---

### Task 9: Install and verify as a local Claude Code plugin

**Files:** none (verification only)

- [ ] **Step 1: Add this repo as a local dev marketplace**

```
/plugin marketplace add /Users/michaelpaulukonis/projects/claude-wikijs-skill
```

Expected: Claude Code confirms the marketplace `claude-wikijs-skill` was added.

- [ ] **Step 2: Install the plugin**

```
/plugin install claude-wikijs-skill@claude-wikijs-skill
```

Then restart Claude Code as prompted.

- [ ] **Step 3: Verify the skill is discoverable**

Start a new session and ask something that should trigger the skill, e.g.
"search my wiki for smoke test". Expected: Claude invokes the `wikijs` skill
(visible via its tool calls) and runs `wikijs.py search ...`.

- [ ] **Step 4: Uninstall the dev install (optional cleanup)**

```
/plugin uninstall claude-wikijs-skill@claude-wikijs-skill
```

Keep it installed if you intend to keep using it from this repo going forward.

---

### Task 10: Tag the 0.1.0 release

**Files:** none

- [ ] **Step 1: Confirm working tree is clean**

Run: `git status`
Expected: `nothing to commit, working tree clean`

- [ ] **Step 2: Tag the release**

```bash
git tag v0.1.0
```

- [ ] **Step 3: Push to GitHub (only after the user has created the remote and confirms)**

Do not run this step without explicit go-ahead — creating the GitHub repo and
pushing publishes it. Once the user confirms a remote exists:

```bash
git remote add origin <github-url>
git push -u origin main
git push origin v0.1.0
```

---

## Deferred (see spec's Future Work section — not part of this plan)

- Full automated CLI test suite (page CRUD, move/rename, assets, tags) against
  a real or mocked Wiki.js instance.
- Multi-editor support (HTML/CKEditor) beyond Markdown.
