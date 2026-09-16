import unittest

from src.application.project import (
    create_project,
    serialize_project,
    sync_project,
)


class ProjectStateAcceptanceTest(unittest.TestCase):

    def test_project_preserves_manuscript(self):
        manuscript = (
            "Jetzt prüfen wir die Linearführung.\n\n"
            "Des werd schon widder!"
        )

        project = create_project(manuscript)

        self.assertEqual(
            project["manuscript"],
            manuscript,
        )

    def test_project_assigns_stable_unit_ids(self):
        project = create_project(
            "Erster Absatz.\n\nZweiter Absatz."
        )

        units = project["units"]

        self.assertEqual(len(units), 2)

        first_id = units[0]["id"]
        second_id = units[1]["id"]

        self.assertIsInstance(first_id, str)
        self.assertIsInstance(second_id, str)

        self.assertTrue(first_id)
        self.assertTrue(second_id)

        self.assertNotEqual(first_id, second_id)

    def test_new_units_use_default_voice(self):
        project = create_project(
            "Erster Absatz.\n\nZweiter Absatz."
        )

        self.assertEqual(
            [unit["voiceId"] for unit in project["units"]],
            [
                "thorsten-high",
                "thorsten-high",
            ],
        )

    def test_serialized_project_contains_user_state(self):
        project = create_project(
            "Jetzt prüfen wir die Maschine.\n\n"
            "Des werd schon widder!"
        )

        project["units"][1]["voiceId"] = (
            "thorsten-hessisch"
        )

        data = serialize_project(project)

        self.assertEqual(data["version"], "1")
        self.assertEqual(
            data["manuscript"],
            project["manuscript"],
        )

        self.assertEqual(
            data["units"][1]["voiceId"],
            "thorsten-hessisch",
        )

    def test_serialized_project_excludes_derived_state(self):
        project = create_project(
            "Die Linearführung wird geprüft."
        )

        # Simulate transient UI/runtime state.
        project["units"][0]["renderText"] = (
            "Die lineare Führung wird geprüft."
        )
        project["units"][0]["audioState"] = "ready"
        project["units"][0]["audioPath"] = (
            "output/001.wav"
        )

        data = serialize_project(project)

        unit = data["units"][0]

        self.assertEqual(
            set(unit.keys()),
            {"id", "voiceId"},
        )

        self.assertNotIn("renderText", unit)
        self.assertNotIn("audioState", unit)
        self.assertNotIn("audioPath", unit)

    def test_inserted_paragraph_preserves_existing_unit_identity(self):
        project = create_project(
            "Absatz A.\n\n"
            "Absatz B.\n\n"
            "Absatz C."
        )

        project["units"][1]["voiceId"] = (
            "thorsten-hessisch"
        )

        original_ids = [
            unit["id"]
            for unit in project["units"]
        ]

        updated = sync_project(
            project,
            "Absatz A.\n\n"
            "Neuer Absatz X.\n\n"
            "Absatz B.\n\n"
            "Absatz C.",
        )

        self.assertEqual(
            updated["units"][0]["id"],
            original_ids[0],
        )

        self.assertNotIn(
            updated["units"][1]["id"],
            original_ids,
        )

        self.assertEqual(
            updated["units"][1]["voiceId"],
            "thorsten-high",
        )

        self.assertEqual(
            updated["units"][2]["id"],
            original_ids[1],
        )

        self.assertEqual(
            updated["units"][2]["voiceId"],
            "thorsten-hessisch",
        )

        self.assertEqual(
            updated["units"][3]["id"],
            original_ids[2],
        )

    def test_deleted_paragraph_does_not_shift_voice(self):
        project = create_project(
            "Absatz A.\n\n"
            "Absatz B.\n\n"
            "Absatz C."
        )

        project["units"][2]["voiceId"] = (
            "thorsten-hessisch"
        )

        original_c_id = project["units"][2]["id"]

        updated = sync_project(
            project,
            "Absatz A.\n\n"
            "Absatz C.",
        )

        self.assertEqual(
            len(updated["units"]),
            2,
        )

        self.assertEqual(
            updated["units"][1]["id"],
            original_c_id,
        )

        self.assertEqual(
            updated["units"][1]["voiceId"],
            "thorsten-hessisch",
        )

    def test_edited_paragraph_preserves_unit_identity_and_voice(self):
        project = create_project(
            "Absatz A.\n\n"
            "Des werd schon widder!\n\n"
            "Absatz C."
        )

        project["units"][1]["voiceId"] = (
            "thorsten-hessisch"
        )

        original_id = project["units"][1]["id"]

        updated = sync_project(
            project,
            "Absatz A.\n\n"
            "Des werd schon wieder!\n\n"
            "Absatz C.",
        )

        self.assertEqual(
            updated["units"][1]["id"],
            original_id,
        )

        self.assertEqual(
            updated["units"][1]["voiceId"],
            "thorsten-hessisch",
        )

    def test_reordered_paragraph_preserves_unit_identity_and_voice(self):
        project = create_project(
            "Absatz A.\n\n"
            "Des werd schon widder!\n\n"
            "Absatz C."
        )

        project["units"][1]["voiceId"] = (
            "thorsten-hessisch"
        )

        original_ids = {
            paragraph: unit["id"]
            for paragraph, unit in zip(
                [
                    "Absatz A.",
                    "Des werd schon widder!",
                    "Absatz C.",
                ],
                project["units"],
            )
        }

        updated = sync_project(
            project,
            "Des werd schon widder!\n\n"
            "Absatz A.\n\n"
            "Absatz C.",
        )

        self.assertEqual(
            updated["units"][0]["id"],
            original_ids["Des werd schon widder!"],
        )

        self.assertEqual(
            updated["units"][0]["voiceId"],
            "thorsten-hessisch",
        )

        self.assertEqual(
            updated["units"][1]["id"],
            original_ids["Absatz A."],
        )

        self.assertEqual(
            updated["units"][2]["id"],
            original_ids["Absatz C."],
        )

    def test_duplicate_paragraphs_preserve_occurrence_order(self):
        project = create_project(
            "Gleicher Absatz.\n\n"
            "Gleicher Absatz.\n\n"
            "Gleicher Absatz."
        )

        project["units"][1]["voiceId"] = (
            "thorsten-hessisch"
        )

        original_ids = [
            unit["id"]
            for unit in project["units"]
        ]

        updated = sync_project(
            project,
            "Gleicher Absatz.\n\n"
            "Gleicher Absatz.",
        )

        self.assertEqual(
            [unit["id"] for unit in updated["units"]],
            original_ids[:2],
        )

        self.assertEqual(
            [unit["voiceId"] for unit in updated["units"]],
            [
                "thorsten-high",
                "thorsten-hessisch",
            ],
        )


if __name__ == "__main__":
    unittest.main()
