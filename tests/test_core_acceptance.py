#!/usr/bin/env python3

import json
import unittest
from pathlib import Path

from src.core.render_units import build_render_units


ROOT = Path(__file__).resolve().parents[1]


class CoreAcceptanceTest(unittest.TestCase):

    def setUp(self):
        self.voices = json.loads(
            (ROOT / "resources/voices.json").read_text(encoding="utf-8")
        )

        self.pronunciation = json.loads(
            (ROOT / "resources/pronunciation.json").read_text(encoding="utf-8")
        )

        self.voice_fixtures = json.loads(
            (
                ROOT
                / "tests/fixtures/voices/golden.json"
            ).read_text(encoding="utf-8")
        )

    def test_golden_render_units(self):
        manuscript = "\n\n".join(
            fixture["text"]
            for fixture in self.voice_fixtures
        )

        voice_plan = {
            f"{index:03d}": fixture["voiceId"]
            for index, fixture in enumerate(
                self.voice_fixtures,
                start=1,
            )
        }

        units = build_render_units(
            manuscript=manuscript,
            pronunciation=self.pronunciation,
            voices=self.voices,
            voice_plan=voice_plan,
        )

        self.assertEqual(len(units), 4)

        self.assertEqual(
            units[0],
            {
                "id": "001",
                "originalText":
                    "Jetzt prüfen wir noch einmal die Ausrichtung "
                    "der Y-Achse.",
                "renderText":
                    "Jetzt prüfen wir noch einmal die Ausrichtung "
                    "der Y-Achse.",
                "voiceId": "thorsten-high",
            },
        )

        self.assertEqual(
            units[1]["voiceId"],
            "thorsten-hessisch",
        )

        self.assertEqual(
            units[1]["originalText"],
            "Ei verbibbsch!",
        )

        self.assertEqual(
            units[2],
            {
                "id": "003",
                "originalText": "Des werd schon widder!",
                "renderText": "Des werd schon widder!",
                "voiceId": "thorsten-hessisch",
            },
        )

        self.assertEqual(
            units[3],
            {
                "id": "004",
                "originalText":
                    "Anschließend können wir mit der Montage "
                    "fortfahren.",
                "renderText":
                    "Anschließend können wir mit der "
                    "[[ mɔnˈtaːʒə ]] fortfahren.",
                "voiceId": "thorsten-high",
            },
        )

    def test_original_manuscript_is_not_modified(self):
        manuscript = (
            "Die Linearführung wird montiert.\n\n"
            "Anschließend beginnt die Montage."
        )

        original = manuscript

        build_render_units(
            manuscript=manuscript,
            pronunciation=self.pronunciation,
            voices=self.voices,
            voice_plan={
                "001": "thorsten-high",
                "002": "thorsten-high",
            },
        )

        self.assertEqual(manuscript, original)


if __name__ == "__main__":
    unittest.main()
