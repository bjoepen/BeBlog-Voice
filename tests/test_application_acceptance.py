import unittest
from pathlib import Path

from src.application.render import render_manuscript


VOICES = {
    "thorsten-high": {
        "name": "Thorsten High",
        "role": "default",
        "modelRef": "de_DE-thorsten-high",
    },
    "thorsten-hessisch": {
        "name": "Thorsten Hessisch",
        "role": "special",
        "modelRef":
            "Thorsten-Voice_Hessisch_Piper_high-Oct2023",
    },
}

PRONUNCIATION = {
    "Linearführung": {
        "type": "rewrite",
        "value": "lineare Führung",
    },
    "Montage": {
        "type": "ipa",
        "value": "mɔnˈtaːʒə",
    },
}


class FakeRuntime:
    def __init__(self):
        self.units = []

    def render(self, unit):
        self.units.append(unit.copy())
        return Path("output") / f"{unit['id']}.wav"


class FailingRuntime:
    def render(self, unit):
        raise RuntimeError("synthetic runtime failure")


class ApplicationAcceptanceTest(unittest.TestCase):

    def test_renders_multiple_paragraphs_in_stable_order(self):
        runtime = FakeRuntime()

        manuscript = (
            "Die Linearführung wird geprüft.\n\n"
            "Anschließend beginnt die Montage."
        )

        result = render_manuscript(
            manuscript=manuscript,
            pronunciation=PRONUNCIATION,
            voices=VOICES,
            runtime=runtime,
        )

        self.assertEqual(
            [unit["id"] for unit in runtime.units],
            ["001", "002"],
        )

        self.assertEqual(
            result,
            [
                {
                    "unitId": "001",
                    "audioPath": Path("output/001.wav"),
                },
                {
                    "unitId": "002",
                    "audioPath": Path("output/002.wav"),
                },
            ],
        )

    def test_uses_default_voice_without_voice_plan(self):
        runtime = FakeRuntime()

        render_manuscript(
            manuscript="Die Linearführung wird geprüft.",
            pronunciation=PRONUNCIATION,
            voices=VOICES,
            runtime=runtime,
        )

        self.assertEqual(
            runtime.units[0]["voiceId"],
            "thorsten-high",
        )

    def test_explicit_voice_plan_reaches_runtime(self):
        runtime = FakeRuntime()

        manuscript = (
            "Jetzt prüfen wir die Maschine.\n\n"
            "Des werd schon widder!"
        )

        render_manuscript(
            manuscript=manuscript,
            pronunciation=PRONUNCIATION,
            voices=VOICES,
            runtime=runtime,
            voice_plan={
                "002": "thorsten-hessisch",
            },
        )

        self.assertEqual(
            runtime.units[0]["voiceId"],
            "thorsten-high",
        )
        self.assertEqual(
            runtime.units[1]["voiceId"],
            "thorsten-hessisch",
        )
        self.assertEqual(
            runtime.units[1]["originalText"],
            "Des werd schon widder!",
        )

    def test_runtime_receives_core_render_text_unchanged(self):
        runtime = FakeRuntime()

        manuscript = (
            "Die Linearführung folgt vor der Montage."
        )

        render_manuscript(
            manuscript=manuscript,
            pronunciation=PRONUNCIATION,
            voices=VOICES,
            runtime=runtime,
        )

        self.assertEqual(
            runtime.units[0]["originalText"],
            manuscript,
        )
        self.assertEqual(
            runtime.units[0]["renderText"],
            "Die lineare Führung folgt vor der "
            "[[ mɔnˈtaːʒə ]].",
        )

    def test_runtime_failure_does_not_mutate_manuscript(self):
        manuscript = (
            "Die Linearführung wird geprüft.\n\n"
            "Des werd schon widder!"
        )

        original = manuscript

        with self.assertRaisesRegex(
            RuntimeError,
            "synthetic runtime failure",
        ):
            render_manuscript(
                manuscript=manuscript,
                pronunciation=PRONUNCIATION,
                voices=VOICES,
                runtime=FailingRuntime(),
                voice_plan={
                    "002": "thorsten-hessisch",
                },
            )

        self.assertEqual(manuscript, original)


if __name__ == "__main__":
    unittest.main()
