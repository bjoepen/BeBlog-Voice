import unittest

from src.application.audio_state import (
    audio_state,
    render_fingerprint,
)


class AudioInvalidationAcceptanceTest(unittest.TestCase):

    def test_unchanged_render_input_remains_ready(self):
        fingerprint = render_fingerprint(
            render_text="Die lineare Führung wird geprüft.",
            voice_id="thorsten-high",
        )

        self.assertEqual(
            audio_state(
                rendered_fingerprint=fingerprint,
                render_text="Die lineare Führung wird geprüft.",
                voice_id="thorsten-high",
            ),
            "ready",
        )

    def test_changed_render_text_becomes_stale(self):
        fingerprint = render_fingerprint(
            render_text="Die lineare Führung wird geprüft.",
            voice_id="thorsten-high",
        )

        self.assertEqual(
            audio_state(
                rendered_fingerprint=fingerprint,
                render_text="Die Linearführung wird geprüft.",
                voice_id="thorsten-high",
            ),
            "stale",
        )

    def test_changed_voice_becomes_stale(self):
        fingerprint = render_fingerprint(
            render_text="Des werd schon widder!",
            voice_id="thorsten-high",
        )

        self.assertEqual(
            audio_state(
                rendered_fingerprint=fingerprint,
                render_text="Des werd schon widder!",
                voice_id="thorsten-hessisch",
            ),
            "stale",
        )

    def test_relevant_pronunciation_change_becomes_stale(self):
        fingerprint = render_fingerprint(
            render_text="Die lineare Führung wird geprüft.",
            voice_id="thorsten-high",
        )

        self.assertEqual(
            audio_state(
                rendered_fingerprint=fingerprint,
                render_text="Die Linear-Führung wird geprüft.",
                voice_id="thorsten-high",
            ),
            "stale",
        )

    def test_irrelevant_dictionary_change_keeps_audio_ready(self):
        fingerprint = render_fingerprint(
            render_text="Die lineare Führung wird geprüft.",
            voice_id="thorsten-high",
        )

        # A dictionary rule for another paragraph does not alter this
        # unit's derived render text and therefore must not invalidate it.
        self.assertEqual(
            audio_state(
                rendered_fingerprint=fingerprint,
                render_text="Die lineare Führung wird geprüft.",
                voice_id="thorsten-high",
            ),
            "ready",
        )

    def test_fingerprint_is_deterministic(self):
        first = render_fingerprint(
            render_text="Montage [[ mɔnˈtaːʒə ]]",
            voice_id="thorsten-high",
        )
        second = render_fingerprint(
            render_text="Montage [[ mɔnˈtaːʒə ]]",
            voice_id="thorsten-high",
        )

        self.assertEqual(first, second)
        self.assertIsInstance(first, str)
        self.assertTrue(first)


if __name__ == "__main__":
    unittest.main()
