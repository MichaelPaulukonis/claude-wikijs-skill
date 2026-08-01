# claude-wikijs-skill

Claude Code skill: a thin CLI wrapper for a Wiki.js **2.x** instance (pages,
search, assets). No MCP server - just a Python script Claude shells out to,
which keeps token overhead low for simple CRUD operations.

## Requirements

- A running Wiki.js **2.x** instance
- An admin API token (Wiki.js Admin -> Users -> API Access)
- Python 3.10+
- `requests` (see Setup)

## Install

Ask Claude Code:

> Install the plugin from https://github.com/MichaelPaulukonis/claude-wikijs-skill

Claude runs the marketplace-add + install steps for you - no manual commands
needed.

Or run those steps yourself:

```bash
/plugin marketplace add MichaelPaulukonis/claude-wikijs-skill
/plugin install claude-wikijs-skill@claude-wikijs-skill
```

Or manually: clone this repo, then symlink/copy its inner `skills/wikijs/`
directory (not the repo root) into `~/.claude/skills/wikijs`, e.g.:

```bash
git clone https://github.com/MichaelPaulukonis/claude-wikijs-skill.git /path/to/clone
ln -s /path/to/clone/skills/wikijs ~/.claude/skills/wikijs
```

Either way, `wikijs.py` still needs `requirements.txt` installed (see Setup) -
run `pip install -r /path/to/clone/requirements.txt` when installing manually.

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

## Quirks (things to be aware of)

Constraints of the Wiki.js 2.x API itself - not fixable client-side:

- **Stale search ids.** `search` hits Wiki.js's search index, which can lag
  behind the live page table after edits/deletes. Trust the returned `path`
  over the `id`; re-resolve via `get` before acting on a search result.
- **Partial write on failed update.** Wiki.js's `pages.update` resolver can
  apply content before running all validations. A failed `update` may have
  already changed the page. `get` to check actual state before retrying.
- **No folder delete.** Confirmed by schema introspection - the `assets`
  mutation type only exposes `createFolder`, `renameAsset`, `deleteAsset`,
  `flushTempUploads`. Nothing to call, no workaround.
- **No asset move-between-folders or metadata edit.** Same introspection
  result. `upload` to the new folder + `delete-asset` the old one is the only
  path today (see Roadmap - this half is fixable).
- **No scoped/read-only API tokens.** Wiki.js 2.x only issues full-admin
  tokens from Admin -> Users -> API Access. `delete`/`delete-asset` require
  `--yes` as the only guard - keep it that way.

## Roadmap

Things the CLI itself could fix, not yet done:

- **Reject `.md`/`.html`/`.txt` uploads client-side.** Wiki.js's router
  treats those extensions as page paths, so the upload succeeds (200) but the
  resulting asset path 404s. `wikijs.py` should refuse these before hitting
  the server instead of letting the trap fire silently.
- **Composite `move-asset` command.** Wrap the current manual
  upload/delete-asset dance (see Quirks above) into one command, and warn
  about pages still embedding the old path.
- **Friendlier empty-content error.** `create`/`update` currently surface
  Wiki.js's raw `"Page content cannot be empty"` error. Point directly at the
  `--content "<!-- -->"` workaround in the error message instead of making
  the user go find it in SKILL.md.
- **Post-failure state check.** On a failed `update`, auto-`get` the page and
  report whether content was actually written, so the "partial write" quirk
  above is at least visible immediately instead of requiring a manual check.

## License

MIT - see `LICENSE`.
