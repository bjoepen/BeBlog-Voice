import unittest

from src.core.voices import (
    get_default_voice_id,
    require_voice,
    validate_voices,
)


VALID = {
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


class VoiceRegistryTest(unittest.TestCase):

    def test_valid_registry(self):
        validate_voices(VALID)

    def test_default_voice(self):
        self.assertEqual(
            get_default_voice_id(VALID),
            "thorsten-high",
        )

    def test_require_known_voice(self):
        voice = require_voice(
            VALID,
            "thorsten-hessisch",
        )

        self.assertEqual(
            voice["name"],
            "Thorsten Hessisch",
        )

    def test_rejects_unknown_voice(self):
        with self.assertRaises(ValueError):
            require_voice(
                VALID,
                "karlsson-kehrt-die-werkstatt",
            )

    def test_rejects_missing_default(self):
        voices = {
            "thorsten-hessisch": {
                "name": "Thorsten Hessisch",
                "role": "special",
                "modelRef": "hessisch",
            }
        }

        with self.assertRaises(ValueError):
            validate_voices(voices)

    def test_rejects_multiple_defaults(self):
        voices = {
            "one": {
                "name": "One",
                "role": "default",
                "modelRef": "one",
            },
            "two": {
                "name": "Two",
                "role": "default",
                "modelRef": "two",
            },
        }

        with self.assertRaises(ValueError):
            validate_voices(voices)


if __name__ == "__main__":
    unittest.main()
