"""T-4387: a test file is never hidden from CI by omission.

`build_tests.yml` and `coverage.yml` named their test files one by one, so
82 of the 138 test files in this tree ran in no workflow at all. A file
added to `test/` ran only if somebody also remembered the workflow line,
and two defects reached a user through that gap (T-4158, T-4196).

`test_path` now names the directory. A file that must not run is excluded
with `--ignore=`, where a reader of the workflow can see it and this test
can check it still points at something real. Silence is no longer a way to
skip a test.
"""
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS = os.path.join(REPO, ".github", "workflows")
TEST_DIR = "test"


def _test_paths(name):
    """The `test_path` tokens a workflow passes, or None when it passes none."""
    path = os.path.join(WORKFLOWS, name)
    with open(path, encoding="utf-8") as handle:
        match = re.search(r'^\s*test_path:\s*"([^"]*)"', handle.read(),
                          re.MULTILINE)
    return match.group(1).split() if match else None


def _workflows_with_a_test_path():
    found = {}
    for name in sorted(os.listdir(WORKFLOWS)):
        if not name.endswith((".yml", ".yaml")):
            continue
        tokens = _test_paths(name)
        if tokens:
            found[name] = tokens
    return found


class TestEveryTestFileReachesCI(unittest.TestCase):

    def test_a_workflow_names_the_directory_not_the_files(self):
        """The rule. Naming files one by one is what hid 82 of them."""
        for name, tokens in _workflows_with_a_test_path().items():
            with self.subTest(workflow=name):
                targets = [t for t in tokens if not t.startswith("--")]
                self.assertEqual(
                    targets, [TEST_DIR],
                    f"{name} names {targets} instead of {TEST_DIR!r}. A file "
                    f"that must not run is excluded with --ignore=, never by "
                    f"leaving it out.")

    def test_every_exclusion_is_explicit_and_real(self):
        """An `--ignore` that points at nothing is a stale exclusion, and
        it reads like a live one."""
        for name, tokens in _workflows_with_a_test_path().items():
            for token in tokens:
                if not token.startswith("--"):
                    continue
                with self.subTest(workflow=name, token=token):
                    self.assertTrue(
                        token.startswith("--ignore="),
                        f"{name}: {token!r} is not an exclusion this test "
                        f"can check")
                    target = token.split("=", 1)[1]
                    self.assertTrue(
                        os.path.exists(os.path.join(REPO, target)),
                        f"{name} ignores {target!r}, which is not in the tree")

    def test_the_workflows_that_run_tests_are_the_ones_expected(self):
        """The control. If `build_tests.yml` or `coverage.yml` stopped
        passing a `test_path`, the two tests above would pass by covering
        nothing."""
        self.assertEqual(sorted(_workflows_with_a_test_path()),
                         ["build_tests.yml", "coverage.yml"])

    def test_the_tree_still_holds_the_files_this_guard_is_for(self):
        """A second control: the guard is worth keeping only while the
        directory really holds more test files than a hand-written list
        would carry."""
        count = sum(len([f for f in files if f.startswith("test_")
                         and f.endswith(".py")])
                    for _, _, files in os.walk(os.path.join(REPO, TEST_DIR)))
        self.assertGreater(count, 100, "the tree lost most of its tests")


if __name__ == "__main__":
    unittest.main()
