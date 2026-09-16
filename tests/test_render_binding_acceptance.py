import unittest

from src.application.project import create_project
from src.application.render_binding import render_project_unit


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

PRONUNCIATION = {
    "Linearführung": {
        "type": "rewrite",
        "value": "lineare Führung",
    }
}


class RecordingRuntime:
    def __init__(self, *, fail=False):
        self.fail = fail
        self.units = []

    def render(self, unit):
        self.units.append(dict(unit))
        if self.fail:
            raise RuntimeError("Piper failed")
        return f"/tmp/{unit['id']}.wav"


class RenderBindingAcceptanceTests(unittest.TestCase):
    def make_project(self):
        project = create_project(
            "Die Linearführung wird geprüft.\n\nDes werd schon widder!"
        )
        project["units"][1]["voiceId"] = "thorsten-hessisch"
        return project

    def test_renders_selected_stable_project_unit_with_current_derived_input(self):
        project = self.make_project()
        stable_id = project["units"][0]["id"]
        runtime = RecordingRuntime()

        result = render_project_unit(
            project=project,
            unit_id=stable_id,
            pronunciation=PRONUNCIATION,
            voices=VOICES,
            runtime=runtime,
        )

        self.assertEqual(len(runtime.units), 1)
        self.assertEqual(runtime.units[0]["id"], "001")
        self.assertEqual(
            runtime.units[0]["renderText"],
            "Die lineare Führung wird geprüft.",
        )
        self.assertEqual(runtime.units[0]["voiceId"], "thorsten-high")
        self.assertEqual(result["unitId"], stable_id)
        self.assertEqual(result["audioState"], "ready")
        self.assertTrue(result["audioPath"].endswith("001.wav"))
        self.assertIn("renderedFingerprint", result)

    def test_stable_identity_maps_to_current_positional_render_unit_and_voice(self):
        project = self.make_project()
        stable_id = project["units"][1]["id"]
        runtime = RecordingRuntime()

        result = render_project_unit(
            project=project,
            unit_id=stable_id,
            pronunciation=PRONUNCIATION,
            voices=VOICES,
            runtime=runtime,
        )

        self.assertEqual(runtime.units[0]["id"], "002")
        self.assertEqual(runtime.units[0]["renderText"], "Des werd schon widder!")
        self.assertEqual(runtime.units[0]["voiceId"], "thorsten-hessisch")
        self.assertEqual(result["unitId"], stable_id)

    def test_failed_render_reports_error_without_mutating_project(self):
        project = self.make_project()
        before = {
            "version": project["version"],
            "manuscript": project["manuscript"],
            "units": [dict(unit) for unit in project["units"]],
        }
        stable_id = project["units"][0]["id"]

        result = render_project_unit(
            project=project,
            unit_id=stable_id,
            pronunciation=PRONUNCIATION,
            voices=VOICES,
            runtime=RecordingRuntime(fail=True),
            previous_audio={
                "renderedFingerprint": "previous-valid-fingerprint",
                "audioPath": "/tmp/previous.wav",
            },
        )

        self.assertEqual(project, before)
        self.assertEqual(result["audioState"], "error")
        self.assertEqual(
            result["renderedFingerprint"],
            "previous-valid-fingerprint",
        )
        self.assertEqual(result["audioPath"], "/tmp/previous.wav")
        self.assertIn("Piper failed", result["error"])

    def test_unknown_stable_unit_id_is_rejected_before_runtime(self):
        runtime = RecordingRuntime()

        with self.assertRaises(ValueError):
            render_project_unit(
                project=self.make_project(),
                unit_id="missing-unit",
                pronunciation=PRONUNCIATION,
                voices=VOICES,
                runtime=runtime,
            )

        self.assertEqual(runtime.units, [])


if __name__ == "__main__":
    unittest.main()
