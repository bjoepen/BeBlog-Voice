import tempfile
import unittest
from pathlib import Path

from src.application.render_binding import render_project_unit
from src.application.project import create_project, sync_project


class WritingRuntime:
    def __init__(self, output: Path):
        self.output = output

    def render(self, unit: dict):
        path = self.output / f"{unit['id']}.wav"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(unit["renderText"], encoding="utf-8")
        return path


class StableAudioArtifactAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.voices = {
            "thorsten-high": {"name": "Thorsten High", "role": "default", "modelRef": "high"},
            "thorsten-hessisch": {"name": "Thorsten Hessisch", "role": "special", "modelRef": "hessisch"},
        }
        self.pronunciation = {}

    def test_successful_render_is_promoted_to_stable_unit_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = create_project("Erster Absatz.\n\nZweiter Absatz.")
            unit_id = project["units"][1]["id"]
            result = render_project_unit(
                project=project,
                unit_id=unit_id,
                pronunciation=self.pronunciation,
                voices=self.voices,
                runtime=WritingRuntime(root / "runtime"),
                artifact_directory=root / "artifacts",
            )
            expected = root / "artifacts" / f"{unit_id}.wav"
            self.assertEqual(Path(result["audioPath"]), expected)
            self.assertEqual(expected.read_text(encoding="utf-8"), "Zweiter Absatz.")

    def test_reordering_does_not_overwrite_other_units_stable_audio(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = create_project("Alpha.\n\nBeta.")
            alpha_id = project["units"][0]["id"]
            beta_id = project["units"][1]["id"]
            runtime = WritingRuntime(root / "runtime")
            alpha = render_project_unit(project=project, unit_id=alpha_id, pronunciation={}, voices=self.voices, runtime=runtime, artifact_directory=root / "artifacts")
            beta = render_project_unit(project=project, unit_id=beta_id, pronunciation={}, voices=self.voices, runtime=runtime, artifact_directory=root / "artifacts")
            alpha_path = Path(alpha["audioPath"])
            beta_path = Path(beta["audioPath"])
            self.assertNotEqual(alpha_path, beta_path)
            self.assertEqual(alpha_path.read_text(encoding="utf-8"), "Alpha.")
            self.assertEqual(beta_path.read_text(encoding="utf-8"), "Beta.")

            changed = sync_project(project, "Neu.\n\nAlpha.\n\nBeta.")
            beta_again = render_project_unit(project=changed, unit_id=beta_id, pronunciation={}, voices=self.voices, runtime=runtime, artifact_directory=root / "artifacts")
            self.assertEqual(Path(beta_again["audioPath"]), beta_path)
            self.assertEqual(alpha_path.read_text(encoding="utf-8"), "Alpha.")
            self.assertEqual(beta_path.read_text(encoding="utf-8"), "Beta.")

    def test_failed_render_preserves_previous_stable_artifact(self):
        class FailingRuntime:
            def render(self, unit):
                raise RuntimeError("kaputt")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = create_project("Alpha.")
            unit_id = project["units"][0]["id"]
            previous = root / "artifacts" / f"{unit_id}.wav"
            previous.parent.mkdir(parents=True)
            previous.write_text("vorher", encoding="utf-8")
            result = render_project_unit(
                project=project,
                unit_id=unit_id,
                pronunciation={}, voices=self.voices,
                runtime=FailingRuntime(), artifact_directory=root / "artifacts",
                previous_audio={"renderedFingerprint": "old", "audioPath": str(previous)},
            )
            self.assertEqual(result["audioState"], "error")
            self.assertEqual(Path(result["audioPath"]), previous)
            self.assertEqual(previous.read_text(encoding="utf-8"), "vorher")


if __name__ == "__main__":
    unittest.main()
