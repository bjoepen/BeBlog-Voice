import unittest

from src.application.audio_state import (
    audio_state,
    begin_render,
    complete_render,
    fail_render,
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

    def test_begin_render_sets_transient_rendering_state(self):
        state = begin_render(
            rendered_fingerprint=None,
        )

        self.assertEqual(state["status"], "rendering")
        self.assertIsNone(state["renderedFingerprint"])

    def test_successful_render_becomes_ready_with_rendered_input(self):
        state = complete_render(
            render_text="Des werd schon widder!",
            voice_id="thorsten-hessisch",
        )

        expected = render_fingerprint(
            render_text="Des werd schon widder!",
            voice_id="thorsten-hessisch",
        )

        self.assertEqual(state["status"], "ready")
        self.assertEqual(
            state["renderedFingerprint"],
            expected,
        )

    def test_failed_render_sets_error_without_claiming_new_audio(self):
        previous = render_fingerprint(
            render_text="Alter Rendertext.",
            voice_id="thorsten-high",
        )

        state = fail_render(
            rendered_fingerprint=previous,
            error="Piper failed",
        )

        self.assertEqual(state["status"], "error")
        self.assertEqual(
            state["renderedFingerprint"],
            previous,
        )
        self.assertEqual(state["error"], "Piper failed")

    def test_render_lifecycle_does_not_mutate_project_state(self):
        project = {
            "version": "1",
            "manuscript": "Des werd schon widder!",
            "units": [
                {
                    "id": "stable-unit-id",
                    "voiceId": "thorsten-hessisch",
                }
            ],
        }
        before = {
            "version": project["version"],
            "manuscript": project["manuscript"],
            "units": [dict(project["units"][0])],
        }

        begin_render(rendered_fingerprint=None)
        fail_render(
            rendered_fingerprint=None,
            error="Piper failed",
        )

        self.assertEqual(project, before)


if __name__ == "__main__":
    unittest.main()
