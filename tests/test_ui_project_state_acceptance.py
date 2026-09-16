import unittest

from src.application.project import create_project, sync_project
from src.application.ui_state import build_ui_state, set_unit_voice


VOICES = {
    "thorsten-high": {
        "name": "Thorsten High",
        "role": "default",
        "modelRef": "de_DE-thorsten-high",
    },
    "thorsten-hessisch": {
        "name": "Thorsten Hessisch",
        "role": "special",
        "modelRef": "Thorsten-Voice_Hessisch_Piper_high-Oct2023",
    },
}


class UiProjectStateAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.manuscript = (
            "Die Linearführung wird vor der Montage geprüft.\n\n"
            "Des werd schon widder!"
        )
        self.project = create_project(self.manuscript)

    def test_view_is_derived_from_project_and_not_a_second_manuscript(self):
        view = build_ui_state(self.project, VOICES)

        self.assertEqual(view["manuscript"], self.manuscript)
        self.assertEqual(len(view["units"]), 2)
        self.assertEqual(view["units"][0]["number"], "001")
        self.assertEqual(
            view["units"][0]["text"],
            "Die Linearführung wird vor der Montage geprüft.",
        )
        self.assertEqual(view["units"][1]["text"], "Des werd schon widder!")
        self.assertNotIn("renderText", view["units"][0])

    def test_view_exposes_stable_project_identity(self):
        view = build_ui_state(self.project, VOICES)

        self.assertEqual(view["units"][0]["id"], self.project["units"][0]["id"])
        self.assertEqual(view["units"][1]["id"], self.project["units"][1]["id"])

    def test_voice_change_is_addressed_by_stable_unit_id(self):
        unit_id = self.project["units"][1]["id"]

        changed = set_unit_voice(
            self.project,
            unit_id=unit_id,
            voice_id="thorsten-hessisch",
            voices=VOICES,
        )
        view = build_ui_state(changed, VOICES)

        self.assertEqual(view["units"][0]["voiceId"], "thorsten-high")
        self.assertEqual(view["units"][1]["voiceId"], "thorsten-hessisch")
        self.assertEqual(view["units"][1]["voiceName"], "Thorsten Hessisch")

    def test_manuscript_sync_preserves_voice_on_matching_paragraph(self):
        unit_id = self.project["units"][1]["id"]
        changed = set_unit_voice(
            self.project,
            unit_id=unit_id,
            voice_id="thorsten-hessisch",
            voices=VOICES,
        )

        synced = sync_project(
            changed,
            "Ein neuer erster Absatz.\n\n" + self.manuscript,
        )
        view = build_ui_state(synced, VOICES)

        hessian = next(unit for unit in view["units"] if unit["id"] == unit_id)
        self.assertEqual(hessian["number"], "003")
        self.assertEqual(hessian["text"], "Des werd schon widder!")
        self.assertEqual(hessian["voiceId"], "thorsten-hessisch")

    def test_unknown_voice_is_rejected_without_mutating_project(self):
        before = [dict(unit) for unit in self.project["units"]]

        with self.assertRaises(ValueError):
            set_unit_voice(
                self.project,
                unit_id=self.project["units"][0]["id"],
                voice_id="unknown-voice",
                voices=VOICES,
            )

        self.assertEqual(self.project["units"], before)


if __name__ == "__main__":
    unittest.main()
