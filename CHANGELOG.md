# Changelog

## 0.1.1 - 2026-08-01

- Fixed manual-install instructions in README (were pointing at the repo root
  instead of the inner `skills/wikijs/` directory).
- Fixed SKILL.md's journal-convention-example reference to use
  `${CLAUDE_PLUGIN_ROOT}` like every other path in the file.
- Removed a leftover "personal" reference from wikijs.py's module docstring.
- Added a regression test for the `update` guard logic (tags-only updates,
  replace+append rejection, no-op rejection) - this exact guard broke once
  during development and had no automated coverage.

## 0.1.0 - 2026-07-31

- Initial extraction from personal dot-files skill collection.
- Generalized install paths for Claude Code plugin use (`${CLAUDE_PLUGIN_ROOT}`).
- Added `update --tags` to set/clear page tags (previously `update` silently
  preserved existing tags only, with no way to change them).
- Documented Wiki.js 2.x-only and Markdown-only limitations explicitly.
