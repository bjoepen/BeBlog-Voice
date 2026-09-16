from pathlib import Path
import json
import tempfile
import unittest

from src.application.project import create_project
from src.application.project_file import load_project_file, save_project_file


class ProjectFileAcceptanceTest(unittest.TestCase):
    def test_save_and_load_preserve_persistent_project_state(self):
        project = create_project("Erster Absatz.\n\nDes werd schon widder!")
        project["units"][1]["voiceId"] = "thorsten-hessisch"

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "werkstatt.bbv"
            save_project_file(path, project)
            restored = load_project_file(path)

        self.assertEqual(restored, project)

    def test_saved_file_contains_only_serialized_project_state(self):
        project = create_project("Ein Absatz.")
        project["units"][0]["audioState"] = "ready"
        project["units"][0]["renderText"] = "abgeleitet"

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "clean.bbv"
            save_project_file(path, project)
            data = json.loads(path.read_text(encoding="utf-8"))

        self.assertNotIn("audioState", data["units"][0])
        self.assertNotIn("renderText", data["units"][0])

    def test_invalid_project_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.bbv"
            path.write_text('{"version":"999","manuscript":"x","units":[]}', encoding="utf-8")

            with self.assertRaises(ValueError):
                load_project_file(path)

    def test_failed_save_does_not_replace_existing_project_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "existing.bbv"
            original = '{"sentinel":true}\n'
            path.write_text(original, encoding="utf-8")

            invalid_project = {"manuscript": 42, "units": []}
            with self.assertRaises(ValueError):
                save_project_file(path, invalid_project)

            self.assertEqual(path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
