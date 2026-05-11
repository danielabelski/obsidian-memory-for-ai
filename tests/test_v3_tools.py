from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
EXAMPLE = REPO / "examples/v3-minimal-vault"


class V3ToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = Path(self.tmp.name) / "vault"
        ignore = shutil.ignore_patterns("__pycache__", ".pytest_cache")
        shutil.copytree(EXAMPLE, self.vault, ignore=ignore)
        self.env = os.environ.copy()
        self.env["MEMORY_TODAY"] = "2026-05-11"
        self.env["PATH"] = f"{Path(sys.executable).parent}{os.pathsep}{self.env.get('PATH', '')}"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_tool(self, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args,
            cwd=self.vault,
            env=self.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=check,
        )

    def lint(self) -> subprocess.CompletedProcess[str]:
        return self.run_tool(sys.executable, "tools/lint.py")

    def assert_lint_error(self, expected: str) -> None:
        result = self.lint()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected, result.stdout)

    def test_clean_reference_vault_lints(self) -> None:
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_missing_schema_version_fails(self) -> None:
        (self.vault / "memory/schema/version.yaml").unlink()
        self.assert_lint_error("missing v3 schema version marker")

    def test_unknown_entity_fails(self) -> None:
        path = self.vault / "memory/facts/elena-voss/base.md"
        path.write_text(path.read_text(encoding="utf-8").replace("entity: elena-voss", "entity: ghost"), encoding="utf-8")
        self.assert_lint_error("unknown entity 'ghost'")

    def test_unknown_predicate_fails(self) -> None:
        path = self.vault / "memory/facts/elena-voss/base.md"
        path.write_text(path.read_text(encoding="utf-8").replace("predicate: base", "predicate: favorite-color"), encoding="utf-8")
        self.assert_lint_error("unknown predicate 'favorite-color'")

    def test_unresolved_wikilink_fails(self) -> None:
        path = self.vault / "memory/people/elena-voss.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[[missing-target]]\n", encoding="utf-8")
        self.assert_lint_error("unresolved wikilink: missing-target")

    def test_ambiguous_wikilink_fails(self) -> None:
        first = self.vault / "memory/context/duplicate.md"
        second = self.vault / "memory/projects/duplicate.md"
        first.write_text("---\ntype: context\ntitle: One\n---\n", encoding="utf-8")
        second.write_text("---\ntype: project\nid: duplicate\ntitle: Two\nstatus: active\n---\n", encoding="utf-8")
        target = self.vault / "memory/people/elena-voss.md"
        target.write_text(target.read_text(encoding="utf-8") + "\n[[duplicate]]\n", encoding="utf-8")
        self.assert_lint_error("ambiguous wikilink: duplicate")

    def test_temporal_contradiction_fails(self) -> None:
        source = self.vault / "memory/facts/elena-voss/base.md"
        conflict = self.vault / "memory/facts/elena-voss/base--conflict.md"
        conflict.write_text(source.read_text(encoding="utf-8").replace('value: "Berlin, Germany"', 'value: "Paris, France"'), encoding="utf-8")
        self.assert_lint_error("contradicts overlapping fact")

    def test_deterministic_view_rebuild(self) -> None:
        self.run_tool(sys.executable, "tools/rebuild_views.py", check=True)
        first = {path.relative_to(self.vault).as_posix(): path.read_text(encoding="utf-8") for path in sorted((self.vault / "memory/_views").rglob("*.md"))}
        shutil.rmtree(self.vault / "memory/_views")
        self.run_tool(sys.executable, "tools/rebuild_views.py", check=True)
        second = {path.relative_to(self.vault).as_posix(): path.read_text(encoding="utf-8") for path in sorted((self.vault / "memory/_views").rglob("*.md"))}
        self.assertEqual(first, second)

    def test_query_facts_and_events(self) -> None:
        facts = self.run_tool("tools/query.sh", "facts", "--entity", "elena-voss", "--predicate", "role", check=True)
        self.assertIn("role = Art conservator and pigment researcher", facts.stdout)
        events = self.run_tool("tools/query.sh", "events", "--since", "2026-03-01", check=True)
        self.assertIn("reviewed concordance progress", events.stdout.lower())

    def test_compact_archives_expired_fact(self) -> None:
        path = self.vault / "memory/facts/elena-voss/base.md"
        text = path.read_text(encoding="utf-8").replace("valid_to: null", "valid_to: 2026-01-01")
        path.write_text(text, encoding="utf-8")
        result = self.run_tool(sys.executable, "tools/compact.py", "--yes")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(path.exists())
        self.assertTrue((self.vault / "memory/_archive/2026/facts/elena-voss/base.md").exists())


if __name__ == "__main__":
    unittest.main()
