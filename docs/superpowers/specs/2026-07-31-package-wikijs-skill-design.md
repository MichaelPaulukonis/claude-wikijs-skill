# Design: Package wikijs skill as a standalone Claude Code plugin

## Context

The `wikijs` skill (thin CLI wrapper for a personal Wiki.js 2.x instance) currently
lives in the `dot-files` repo at `claude/skills/wikijs/`, symlinked into
`~/.claude/skills/wikijs`. It's personal-use only: hardcoded assumptions about a
journaling convention, install paths that assume `~/.claude/skills/wikijs`, and no
onboarding docs for anyone else's Wiki.js instance.

Goal: extract it into its own public GitHub repo, packaged as an installable Claude
Code plugin, usable by anyone running Wiki.js **2.x** (not 3.x, which is a different,
still-beta GraphQL schema).

## Repo relationship

- New repo: `claude-wikijs-skill` at `~/projects/claude-wikijs-skill`, MIT licensed.
- `dot-files` keeps its own copy of the skill running in parallel during the
  transition — no symlink or submodule for now. Once the plugin-installed version
  is proven stable, `dot-files` switches to installing it as a plugin and its local
  copy is removed. This is a deliberate, temporary duplication; not addressed further
  in this spec.

## Repo layout

```
claude-wikijs-skill/
├── .claude-plugin/
│   ├── plugin.json          # plugin manifest
│   └── marketplace.json     # self-referencing dev/distribution marketplace (source: "./")
├── skills/
│   └── wikijs/
│       ├── SKILL.md
│       └── scripts/
│           └── wikijs.py
├── docs/
│   ├── journal-convention-example.md
│   └── superpowers/specs/   # this file
├── requirements.txt          # requests>=2.x
├── .env.example              # WIKIJS_API_URL=, WIKIJS_TOKEN=
├── README.md
├── LICENSE                   # MIT
└── CHANGELOG.md
```

Single-repo plugin+marketplace pattern: `.claude-plugin/marketplace.json` lists this
plugin with `"source": "./"`, so the same repo serves as both the plugin and its own
marketplace. Users install with:

```
/plugin marketplace add <owner>/claude-wikijs-skill
/plugin install claude-wikijs-skill@claude-wikijs-skill
```

`.claude-plugin/` contains only the two manifest files — no skills or scripts inside
it, per Claude Code plugin conventions.

## Component: `wikijs.py`

No functional rewrite. The script is already environment-driven
(`WIKIJS_API_URL`, `WIKIJS_TOKEN`, `WIKIJS_MAX_UPLOAD_BYTES`), contains no secrets,
and has no personal-specific logic — it's a generic Wiki.js 2.x GraphQL/REST client.
Ship it unchanged from `dot-files/claude/skills/wikijs/scripts/wikijs.py`.

Dependency: `requests`. Declared in `requirements.txt`
(`requests>=2.28`). README documents a one-time
`pip install -r requirements.txt` setup step. (Considered rewriting to stdlib
`urllib` to drop the dependency; rejected — the multipart upload in `cmd_upload`
would need a hand-rolled encoder, which is more risk than a one-line `pip install`
is worth.)

One functional fix, made now as part of this packaging pass (not deferred):
**`update` currently cannot change tags.** It fetches the page's existing tags and
passes them straight back unchanged (see the comment at `wikijs.py:99-101`) — there
is no way to add, remove, or replace tags via the CLI today. Add a `--tags`
flag to `update`, matching `create`'s comma-separated syntax:

- `update <ref> --tags a,b,c` — replaces the page's tag list with `[a, b, c]`
- `--tags ""` — clears all tags
- `--tags` omitted — current behavior unchanged (existing tags preserved)
- Combinable with `--append`/`--replace`/`--append-file`/`--replace-file` in the
  same invocation, since tags and content are independent fields on the same
  mutation.

## Component: `SKILL.md`

Adapted from the current `dot-files` version with these changes:

1. **Remove the "Journal convention" section entirely.** It encodes one person's
   habitual page-naming scheme (`journal/{year}/{month}/{day}-{weekday}`, etc.) and
   doesn't belong in a generic public skill. Moved to
   `docs/journal-convention-example.md`, explicitly framed as an example to copy and
   adapt, not a fixed convention.
2. **Generalize the install path.** Replace hardcoded
   `~/.claude/skills/wikijs/scripts/wikijs.py` with
   `${CLAUDE_PLUGIN_ROOT}/skills/wikijs/scripts/wikijs.py` so it resolves correctly
   regardless of where the plugin is installed.
3. **Add a one-time dependency install step** to Setup:
   `pip install -r requirements.txt` (path also relative to `${CLAUDE_PLUGIN_ROOT}`).
4. **Add an explicit version-compatibility warning** near the top:
   > Wiki.js 2.x only. This wraps the 2.x GraphQL schema (`pages.singleByPath`,
   > `assets.folders`, etc). Wiki.js 3.x uses a different, still-beta schema and is
   > not supported.
5. **Add an explicit markup-support note:** pages are created/updated with
   `editor: "markdown"` hardcoded (`wikijs.py:82`, `:117`) — this skill only
   supports Markdown-edited pages today, even though Wiki.js 2.x also offers
   HTML and CKEditor page editors. Document this as a current limitation, with a
   pointer to the Future Work section below (not fixed in this pass).
6. **Document the new `update --tags` flag** (see `wikijs.py` component above) in
   the Commands reference.
7. **Keep the rest of the "Commands" and "Quirks" sections as-is.** These document
   genuine 2.x API behavior (stale search ids, no folder delete, asset move
   workaround, `.md` upload trap, etc.) — useful to any user of this skill, not
   personal habit.

## Component: `docs/journal-convention-example.md`

Contains the extracted journal convention section verbatim, reframed:

- Heading: "Example: daily journal convention"
- Intro line: "This is one convention for journaling with this skill — adapt paths,
  titles, and section structure to your own wiki. Nothing here is enforced by
  `wikijs.py`."
- Same content as before (entry path format, title format, parent page structure,
  journaling flow, link-formatting note) as a worked example.

## Component: `.env.example`

```
WIKIJS_API_URL=http://localhost
WIKIJS_TOKEN=
```

Mirrors the real `~/.config/wikijs.env` shape (verified: currently just these two
vars). README instructs copying this to `~/.config/wikijs.env` and filling in a
token generated from Wiki.js Admin → Users → API Access.

## Component: `README.md`

Sections:

- What it is: thin CLI wrapper for Wiki.js 2.x, no MCP server, avoids MCP tool-call
  token overhead for simple CRUD.
- Requirements: a running Wiki.js **2.x** instance, an admin API token, Python 3,
  `requests`.
- Install as a Claude Code plugin (marketplace add/install commands) or manually by
  cloning into `~/.claude/skills/`.
- Config: copy `.env.example` to `~/.config/wikijs.env`, fill in `WIKIJS_API_URL`
  and `WIKIJS_TOKEN`.
- Usage: point to `SKILL.md` for the full command reference.
- Link to `docs/journal-convention-example.md` as an optional pattern.
- License: MIT.

## Component: `plugin.json` / `marketplace.json`

Minimal manifests per Claude Code plugin conventions:

`plugin.json`:
```json
{
  "name": "claude-wikijs-skill",
  "version": "0.1.0",
  "description": "Claude Code skill: CLI wrapper for a Wiki.js 2.x instance (pages, search, assets)",
  "author": { "name": "Michael Paulukonis" },
  "license": "MIT"
}
```

`marketplace.json`:
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

## Future work (deferred until this packaging pass is done and working)

- **Test suite** covering the CLI end-to-end against a real Wiki.js 2.x instance:
  create/get/update/search/list/delete for pages, tag add/modify (once `--tags`
  ships), move/rename, upload/assets/delete-asset/rename-asset. No test framework
  chosen yet — pick one when this work starts.
- **Multi-editor support**: add HTML/CKEditor page support (currently hardcoded to
  `editor: "markdown"`), with tests covering each supported editor type.

Both are real, wanted follow-ups — just sequenced after the base packaging/release
work in this spec, not blocking it.

## Out of scope

- Migrating `dot-files` to install this as a plugin (deferred until the standalone
  version is proven).
- Wiki.js 3.x support.
- Publishing to any Claude Code plugin marketplace listing beyond the repo's own
  self-referencing marketplace.
