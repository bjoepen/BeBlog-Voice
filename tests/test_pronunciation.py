import unittest

from src.core.pronunciation import apply_pronunciation


class PronunciationTest(unittest.TestCase):

    def test_rewrite(self):
        pronunciation = {
            "Linearführung": {
                "type": "rewrite",
                "value": "lineare Führung",
            }
        }

        self.assertEqual(
            apply_pronunciation(
                "Die Linearführung wird montiert.",
                pronunciation,
            ),
            "Die lineare Führung wird montiert.",
        )

    def test_ipa(self):
        pronunciation = {
            "Montage": {
                "type": "ipa",
                "value": "mɔnˈtaːʒə",
            }
        }

        self.assertEqual(
            apply_pronunciation(
                "Wir beginnen mit der Montage.",
                pronunciation,
            ),
            "Wir beginnen mit der [[ mɔnˈtaːʒə ]].",
        )

    def test_unknown_words_remain_unchanged(self):
        self.assertEqual(
            apply_pronunciation(
                "Des werd schon widder!",
                {},
            ),
            "Des werd schon widder!",
        )

    def test_source_text_is_not_modified(self):
        text = "Die Linearführung."
        original = text

        apply_pronunciation(
            text,
            {
                "Linearführung": {
                    "type": "rewrite",
                    "value": "lineare Führung",
                }
            },
        )

        self.assertEqual(text, original)

    def test_does_not_replace_inside_other_words(self):
        pronunciation = {
            "CNC": {
                "type": "rewrite",
                "value": "Zeh Enn Zeh",
            }
        }

        self.assertEqual(
            apply_pronunciation(
                "CNCTest bleibt unverändert.",
                pronunciation,
            ),
            "CNCTest bleibt unverändert.",
        )

    def test_rejects_unknown_rule_type(self):
        with self.assertRaises(ValueError):
            apply_pronunciation(
                "Montage",
                {
                    "Montage": {
                        "type": "magic",
                        "value": "irgendwas",
                    }
                },
            )


if __name__ == "__main__":
    unittest.main()
