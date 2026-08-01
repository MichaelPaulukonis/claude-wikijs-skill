import argparse
import sys
from pathlib import Path

import pytest

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


class FakeGql:
    """Stands in for wikijs.gql() so cmd_update tests never hit the network."""

    def __init__(self, page_content="original", page_tags=None):
        self.page_content = page_content
        self.page_tags = page_tags or []
        self.calls = []

    def __call__(self, query, variables=None):
        self.calls.append((query, variables))
        if "single(id:" in query:
            return {
                "pages": {
                    "single": {
                        "content": self.page_content,
                        "tags": [{"tag": t} for t in self.page_tags],
                    }
                }
            }
        if "update(id:" in query:
            return {
                "pages": {"update": {"responseResult": {"succeeded": True, "message": ""}}}
            }
        raise AssertionError(f"unexpected query: {query}")


def make_update_args(**overrides):
    defaults = dict(
        ref="123", replace=None, replace_file=None, append=None, append_file=None, tags=None
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_cmd_update_tags_only_does_not_die(monkeypatch):
    # Regression test: this exact case (--tags with no --replace/--append) used
    # to hit the old "pass exactly one of --replace/.../--append-file" guard
    # and die() even though tags-only updates are the flag's primary use case.
    fake = FakeGql(page_content="original", page_tags=["old"])
    monkeypatch.setattr(wikijs, "gql", fake)
    wikijs.cmd_update(make_update_args(tags="new"))
    _, mutation_vars = fake.calls[1]
    assert mutation_vars["tags"] == ["new"]
    assert mutation_vars["content"] == "original"


def test_cmd_update_append_only_still_works(monkeypatch):
    fake = FakeGql(page_content="original", page_tags=["old"])
    monkeypatch.setattr(wikijs, "gql", fake)
    wikijs.cmd_update(make_update_args(append="more"))
    _, mutation_vars = fake.calls[1]
    assert mutation_vars["content"] == "original\n\nmore\n"
    assert mutation_vars["tags"] == ["old"]


def test_cmd_update_replace_and_append_together_dies(monkeypatch):
    fake = FakeGql()
    monkeypatch.setattr(wikijs, "gql", fake)
    with pytest.raises(SystemExit):
        wikijs.cmd_update(make_update_args(replace="x", append="y"))


def test_cmd_update_nothing_given_dies(monkeypatch):
    fake = FakeGql()
    monkeypatch.setattr(wikijs, "gql", fake)
    with pytest.raises(SystemExit):
        wikijs.cmd_update(make_update_args())
