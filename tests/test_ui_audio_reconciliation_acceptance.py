import unittest
from pathlib import Path

from src.application.audio_state import complete_render
from src.application.project import create_project, sync_project
from src.application.ui_state import build_ui_state, set_unit_voice


ROOT = Path(__file__).resolve().parents[1]


class AudioReconciliationAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.voices = {
            "thorsten-high": {"name": "Thorsten High", "role": "default", "modelRef": "high"},
            "thorsten-hessisch": {"name": "Thorsten Hessisch", "role": "special", "modelRef": "hessisch"},
        }
        self.pronunciation = {
            "Linearführung": {"type": "rewrite", "value": "lineare Führung"},
        }

    def test_ready_audio_remains_ready_for_unchanged_render_input(self):
        project = create_project("Die Linearführung wird geprüft.")
        rendered = complete_render(render_text="Die lineare Führung wird geprüft.", voice_id="thorsten-high")
        audio = {project["units"][0]["id"]: {**rendered, "audioPath": "/tmp/unit.wav"}}

        view = build_ui_state(project, self.voices, pronunciation=self.pronunciation, audio_by_unit=audio)

        self.assertEqual(view["units"][0]["audioState"], "ready")
        self.assertEqual(view["units"][0]["audioPath"], "/tmp/unit.wav")

    def test_manuscript_change_marks_existing_audio_stale(self):
        project = create_project("Die Linearführung wird geprüft.")
        unit_id = project["units"][0]["id"]
        rendered = complete_render(render_text="Die lineare Führung wird geprüft.", voice_id="thorsten-high")
        audio = {unit_id: {**rendered, "audioPath": "/tmp/unit.wav"}}
        changed = sync_project(project, "Die Linearführung wird erneut geprüft.")

        view = build_ui_state(changed, self.voices, pronunciation=self.pronunciation, audio_by_unit=audio)

        self.assertEqual(view["units"][0]["id"], unit_id)
        self.assertEqual(view["units"][0]["audioState"], "stale")

    def test_voice_change_marks_existing_audio_stale(self):
        project = create_project("Des werd schon widder!")
        unit_id = project["units"][0]["id"]
        rendered = complete_render(render_text="Des werd schon widder!", voice_id="thorsten-high")
        audio = {unit_id: {**rendered, "audioPath": "/tmp/unit.wav"}}
        changed = set_unit_voice(project, unit_id=unit_id, voice_id="thorsten-hessisch", voices=self.voices)

        view = build_ui_state(changed, self.voices, pronunciation=self.pronunciation, audio_by_unit=audio)

        self.assertEqual(view["units"][0]["audioState"], "stale")

    def test_ui_does_not_compute_fingerprints(self):
        source = (ROOT / "ui/src/App.svelte").read_text(encoding="utf-8")
        self.assertNotIn("render_fingerprint", source)
        self.assertNotIn("sha256", source)
        self.assertNotIn("renderText", source)


if __name__ == "__main__":
    unittest.main()
