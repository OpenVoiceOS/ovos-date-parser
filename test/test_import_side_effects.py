"""Importing the package writes nothing to disk and builds no phrase tables.

ovos-config creates its configuration folder when it is imported, so the
package imports it only in the functions that read the configuration. The
era patterns and the English scoped vocabulary compile hundreds of phrase
sets; they are built the first time an extractor needs them."""
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest

PROBE = textwrap.dedent("""
    import json, sys
    calls = []

    def profile(frame, event, arg):
        if event == "call" and frame.f_code.co_name in (
                "load_era_patterns", "load_scoped_vocabulary"):
            calls.append(frame.f_code.co_name)

    sys.setprofile(profile)
    import ovos_date_parser
    sys.setprofile(None)
    at_import = list(calls)
    has_config = "ovos_config" in sys.modules

    sys.setprofile(profile)
    from ovos_date_parser.eras_en import extract_era_date_en
    era = extract_era_date_en("caesar died in 44 BC")
    sys.setprofile(None)
    print(json.dumps({"at_import": at_import, "ovos_config": has_config,
                      "after_use": calls[len(at_import):],
                      "era_year": era[0].year}))
""")


class TestImportSideEffects(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.home = tempfile.TemporaryDirectory()
        env = dict(os.environ)
        for var in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME",
                    "XDG_CACHE_HOME"):
            env.pop(var, None)
        env["HOME"] = cls.home.name
        out = subprocess.run([sys.executable, "-c", PROBE], env=env,
                             capture_output=True, text=True, check=True)
        cls.probe = json.loads(out.stdout.strip().splitlines()[-1])

    @classmethod
    def tearDownClass(cls):
        cls.home.cleanup()

    def test_import_writes_nothing_to_home(self):
        written = [os.path.relpath(os.path.join(root, name), self.home.name)
                   for root, dirs, files in os.walk(self.home.name)
                   for name in dirs + files]
        self.assertEqual(written, [])

    def test_import_does_not_load_ovos_config(self):
        self.assertFalse(self.probe["ovos_config"])

    def test_import_builds_no_phrase_tables(self):
        self.assertEqual(self.probe["at_import"], [])

    def test_first_use_builds_the_table_once(self):
        self.assertEqual(self.probe["after_use"], ["load_era_patterns"])
        # 44 BC is astronomical year 1 - 44 = -43 (ISO 8601 numbering)
        self.assertEqual(self.probe["era_year"], -43)


if __name__ == "__main__":
    unittest.main()
