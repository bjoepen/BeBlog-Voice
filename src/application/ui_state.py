from copy import deepcopy

from src.core.manuscript import split_paragraphs
from src.core.voices import require_voice, validate_voices


def build_ui_state(project: dict, voices: dict) -> dict:
    if not isinstance(project, dict):
        raise TypeError("project must be a dictionary")

    validate_voices(voices)

    manuscript = project.get("manuscript")
    project_units = project.get("units")

    if not isinstance(manuscript, str):
        raise ValueError("project requires manuscript")

    if not isinstance(project_units, list):
        raise ValueError("project requires units")

    paragraphs = split_paragraphs(manuscript)

    if len(paragraphs) != len(project_units):
        raise ValueError("project units do not match manuscript")

    units = []

    for index, (paragraph, project_unit) in enumerate(
        zip(paragraphs, project_units),
        start=1,
    ):
        if not isinstance(project_unit, dict):
            raise ValueError("project unit must be a dictionary")

        unit_id = project_unit.get("id")
        voice_id = project_unit.get("voiceId")

        if not isinstance(unit_id, str) or not unit_id:
            raise ValueError("project unit requires stable id")

        voice = require_voice(voices, voice_id)

        units.append(
            {
                "id": unit_id,
                "number": f"{index:03d}",
                "text": paragraph,
                "voiceId": voice_id,
                "voiceName": voice["name"],
                "audioState": "idle",
            }
        )

    return {
        "manuscript": manuscript,
        "units": units,
    }


def set_unit_voice(
    project: dict,
    *,
    unit_id: str,
    voice_id: str,
    voices: dict,
) -> dict:
    if not isinstance(project, dict):
        raise TypeError("project must be a dictionary")

    require_voice(voices, voice_id)

    units = project.get("units")

    if not isinstance(units, list):
        raise ValueError("project requires units")

    changed = deepcopy(project)

    for unit in changed["units"]:
        if unit.get("id") == unit_id:
            unit["voiceId"] = voice_id
            return changed

    raise ValueError(f"unknown project unit ID: {unit_id!r}")
