import unittest

from src.core.manuscript import split_paragraphs


class ManuscriptTest(unittest.TestCase):

    def test_split_paragraphs(self):
        manuscript = (
            "Absatz eins.\n\n"
            "Absatz zwei.\n\n"
            "Absatz drei."
        )

        self.assertEqual(
            split_paragraphs(manuscript),
            [
                "Absatz eins.",
                "Absatz zwei.",
                "Absatz drei.",
            ],
        )

    def test_ignores_empty_paragraphs(self):
        manuscript = (
            "\n\n"
            "Absatz eins.\n"
            "\n\n"
            "Absatz zwei.\n\n"
        )

        self.assertEqual(
            split_paragraphs(manuscript),
            [
                "Absatz eins.",
                "Absatz zwei.",
            ],
        )

    def test_does_not_modify_input(self):
        manuscript = "Original eins.\n\nOriginal zwei."
        original = manuscript

        split_paragraphs(manuscript)

        self.assertEqual(manuscript, original)

    def test_rejects_non_string_input(self):
        with self.assertRaises(TypeError):
            split_paragraphs(None)


if __name__ == "__main__":
    unittest.main()
