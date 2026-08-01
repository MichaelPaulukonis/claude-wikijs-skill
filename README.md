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
