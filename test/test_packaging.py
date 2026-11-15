import ast
import re
import sys
import unittest
from importlib.metadata import packages_distributions
from importlib.metadata import version as installed_version
from importlib.resources import files
from pathlib import Path

from ovos_date_parser.version import (VERSION_ALPHA, VERSION_BUILD, VERSION_MAJOR,
                           VERSION_MINOR, __version__)

VERSION_FILE = Path(__file__).parent.parent / "ovos_date_parser" / "version.py"
PYPROJECT = Path(__file__).parent.parent / "pyproject.toml"


def _canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


class TestVersionBlock(unittest.TestCase):
    """The release automation rewrites version.py by pattern, and the build
    backend reads __version__ from it. Both contracts are asserted here."""

    def test_version_block_markers_present(self):
        text = VERSION_FILE.read_text()
        self.assertIn("# START_VERSION_BLOCK", text)
        self.assertIn("# END_VERSION_BLOCK", text)

    def test_version_block_holds_four_plain_integers(self):
        # the bumper rewrites these by regex; they must stay bare int literals
        block = VERSION_FILE.read_text().split("# END_VERSION_BLOCK")[0]
        assigned = {
            node.targets[0].id: node.value
            for node in ast.parse(block).body
            if isinstance(node, ast.Assign)
        }
        self.assertEqual(
            sorted(assigned),
            ["VERSION_ALPHA", "VERSION_BUILD", "VERSION_MAJOR", "VERSION_MINOR"],
        )
        for name, value in assigned.items():
            self.assertIsInstance(value, ast.Constant, f"{name} must be a literal")
            self.assertIsInstance(value.value, int, f"{name} must be an int")

    def test_version_string_matches_version_block(self):
        expected = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
        if VERSION_ALPHA:
            expected += f"a{VERSION_ALPHA}"
        self.assertEqual(__version__, expected)

    def test_alpha_suffix_only_when_alpha_is_set(self):
        self.assertEqual("a" in __version__, bool(VERSION_ALPHA))

    def test_installed_metadata_matches_source(self):
        # catches a pyproject that stops tracking version.py
        self.assertEqual(installed_version("ovos-date-parser"), __version__)


class TestPackagedResources(unittest.TestCase):
    """res/ is data, not code, so it only ships if package-data says so."""

    def test_resources_are_reachable_as_package_data(self):
        res = files("ovos_date_parser") / "res"
        self.assertTrue(res.is_dir(), "res/ missing from the installed package")

    def test_every_res_json_in_the_tree_is_packaged(self):
        root = Path(__file__).parent.parent / "ovos_date_parser"
        on_disk = {p.relative_to(root) for p in root.glob("res/**/*.json")}
        self.assertTrue(on_disk, "no res json found to check")
        packaged = files("ovos_date_parser")
        missing = sorted(str(p) for p in on_disk
                         if not (packaged / str(p)).is_file())
        self.assertEqual(missing, [], "res files not packaged")


class TestDeclaredDependencies(unittest.TestCase):
    """A package the code imports but does not declare can resolve to any
    version, or to one that lacks the imported module."""

    def test_every_imported_distribution_is_declared(self):
        block = PYPROJECT.read_text(encoding="utf-8").split("\ndependencies = [", 1)[1].split("\n]", 1)[0]
        declared = {_canonical(m) for m in re.findall(r'^\s*"([A-Za-z0-9_.-]+)', block, re.M)}
        imported = set()
        for path in (PYPROJECT.parent / "ovos_date_parser").rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    imported.add(node.module.split(".")[0])
        imported -= set(sys.stdlib_module_names) | {"ovos_date_parser"}
        distributions = packages_distributions()
        needed = {_canonical(dist) for name in imported for dist in distributions.get(name, [name])}
        self.assertEqual(sorted(needed - declared), [])


if __name__ == "__main__":
    unittest.main()
