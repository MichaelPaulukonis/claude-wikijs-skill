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
