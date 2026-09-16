import json
import unittest

from src.application.project import (
    create_project,
    deserialize_project,
    serialize_project,
)


class ProjectPersistenceAcceptanceTest(unittest.TestCase):

    def test_round_trip_preserves_manuscript_ids_and_voice_decisions(self):
        manuscript = (
            "Die Linearführung wird geprüft.\n\n"
            "Des werd schon widder!"
        )
        project = create_project(manuscript)
        project["units"][1]["voiceId"] = "thorsten-hessisch"

        serialized = serialize_project(project)
        encoded = json.dumps(serialized, ensure_ascii=False)
        decoded = json.loads(encoded)
        restored = deserialize_project(decoded)

        self.assertEqual(restored["version"], project["version"])
        self.assertEqual(restored["manuscript"], manuscript)
        self.assertEqual(
            [unit["id"] for unit in restored["units"]],
            [unit["id"] for unit in project["units"]],
        )
        self.assertEqual(
            [unit["voiceId"] for unit in restored["units"]],
            ["thorsten-high", "thorsten-hessisch"],
        )

    def test_deserialization_rejects_unknown_project_version(self):
        data = {
            "version": "999",
            "manuscript": "Des werd schon widder!",
            "units": [
                {
                    "id": "stable-unit-id",
                    "voiceId": "thorsten-hessisch",
                }
            ],
        }

        with self.assertRaises(ValueError):
            deserialize_project(data)

    def test_deserialization_rejects_unit_count_mismatch(self):
        data = {
            "version": "1",
            "manuscript": "Absatz eins.\n\nAbsatz zwei.",
            "units": [
                {
                    "id": "only-one-unit",
                    "voiceId": "thorsten-high",
                }
            ],
        }

        with self.assertRaises(ValueError):
            deserialize_project(data)

    def test_deserialization_rejects_missing_stable_identity(self):
        data = {
            "version": "1",
            "manuscript": "Des werd schon widder!",
            "units": [
                {
                    "voiceId": "thorsten-hessisch",
                }
            ],
        }

        with self.assertRaises(ValueError):
            deserialize_project(data)

    def test_deserialization_rejects_missing_voice_decision(self):
        data = {
            "version": "1",
            "manuscript": "Des werd schon widder!",
            "units": [
                {
                    "id": "stable-unit-id",
                }
            ],
        }

        with self.assertRaises(ValueError):
            deserialize_project(data)

    def test_persistence_excludes_derived_and_audio_state(self):
        project = create_project("Die Linearführung wird geprüft.")
        project["units"][0].update(
            {
                "renderText": "Die lineare Führung wird geprüft.",
                "audioState": "ready",
                "audioPath": "/tmp/001.wav",
                "renderedFingerprint": "abc123",
            }
        )

        serialized = serialize_project(project)
        restored = deserialize_project(serialized)

        unit = restored["units"][0]
        self.assertEqual(set(unit), {"id", "voiceId"})
        self.assertNotIn("renderText", unit)
        self.assertNotIn("audioState", unit)
        self.assertNotIn("audioPath", unit)
        self.assertNotIn("renderedFingerprint", unit)

    def test_project_round_trip_requires_no_runtime_or_models(self):
        project = create_project("Des werd schon widder!")
        serialized = serialize_project(project)

        restored = deserialize_project(serialized)

        self.assertEqual(restored, serialized)


if __name__ == "__main__":
    unittest.main()
