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
