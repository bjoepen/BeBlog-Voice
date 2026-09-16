from copy import deepcopy
from uuid import uuid4

from src.core.manuscript import split_paragraphs


PROJECT_VERSION = "1"
DEFAULT_VOICE_ID = "thorsten-high"


def _new_unit() -> dict:
    return {
        "id": str(uuid4()),
        "voiceId": DEFAULT_VOICE_ID,
    }


def create_project(manuscript: str) -> dict:
    paragraphs = split_paragraphs(manuscript)

    return {
        "version": PROJECT_VERSION,
        "manuscript": manuscript,
        "units": [
            _new_unit()
            for _paragraph in paragraphs
        ],
    }


def serialize_project(project: dict) -> dict:
    if not isinstance(project, dict):
        raise TypeError(
            "project must be a dictionary"
        )

    manuscript = project.get("manuscript")
    units = project.get("units")

    if not isinstance(manuscript, str):
        raise ValueError(
            "project requires manuscript"
        )

    if not isinstance(units, list):
        raise ValueError(
            "project requires units"
        )

    serialized_units = []

    for unit in units:
        serialized_units.append(
            {
                "id": unit["id"],
                "voiceId": unit["voiceId"],
            }
        )

    return {
        "version": PROJECT_VERSION,
        "manuscript": manuscript,
        "units": deepcopy(serialized_units),
    }


def deserialize_project(data: dict) -> dict:
    if not isinstance(data, dict):
        raise TypeError(
            "project data must be a dictionary"
        )

    if data.get("version") != PROJECT_VERSION:
        raise ValueError(
            "unsupported project version"
        )

    manuscript = data.get("manuscript")
    units = data.get("units")

    if not isinstance(manuscript, str):
        raise ValueError(
            "project requires manuscript"
        )

    if not isinstance(units, list):
        raise ValueError(
            "project requires units"
        )

    paragraphs = split_paragraphs(manuscript)

    if len(paragraphs) != len(units):
        raise ValueError(
            "project units do not match manuscript"
        )

    restored_units = []

    for unit in units:
        if not isinstance(unit, dict):
            raise ValueError(
                "project unit must be a dictionary"
            )

        unit_id = unit.get("id")
        voice_id = unit.get("voiceId")

        if not isinstance(unit_id, str) or not unit_id:
            raise ValueError(
                "project unit requires stable id"
            )

        if not isinstance(voice_id, str) or not voice_id:
            raise ValueError(
                "project unit requires voiceId"
            )

        restored_units.append(
            {
                "id": unit_id,
                "voiceId": voice_id,
            }
        )

    return {
        "version": PROJECT_VERSION,
        "manuscript": manuscript,
        "units": deepcopy(restored_units),
    }


def sync_project(
    project: dict,
    manuscript: str,
) -> dict:
    if not isinstance(project, dict):
        raise TypeError(
            "project must be a dictionary"
        )

    if not isinstance(manuscript, str):
        raise TypeError(
            "manuscript must be a string"
        )

    old_manuscript = project.get("manuscript")
    old_units = project.get("units")

    if not isinstance(old_manuscript, str):
        raise ValueError(
            "project requires manuscript"
        )

    if not isinstance(old_units, list):
        raise ValueError(
            "project requires units"
        )

    old_paragraphs = split_paragraphs(
        old_manuscript
    )
    new_paragraphs = split_paragraphs(
        manuscript
    )

    if len(old_paragraphs) != len(old_units):
        raise ValueError(
            "project units do not match manuscript"
        )

    new_units = [None] * len(new_paragraphs)
    used_old = set()

    # Pass 1: preserve exact paragraph identity even when moved.
    for new_index, paragraph in enumerate(new_paragraphs):
        for old_index, old_paragraph in enumerate(old_paragraphs):
            if old_index in used_old:
                continue

            if paragraph == old_paragraph:
                new_units[new_index] = deepcopy(
                    old_units[old_index]
                )
                used_old.add(old_index)
                break

    # Pass 2: unmatched paragraph at the same structural position is
    # treated as an edited paragraph and keeps its user state.
    for new_index in range(len(new_paragraphs)):
        if new_units[new_index] is not None:
            continue

        if (
            new_index < len(old_units)
            and new_index not in used_old
        ):
            new_units[new_index] = deepcopy(
                old_units[new_index]
            )
            used_old.add(new_index)

    # Pass 3: anything still unmatched is genuinely new.
    for new_index in range(len(new_units)):
        if new_units[new_index] is None:
            new_units[new_index] = _new_unit()

    return {
        "version": PROJECT_VERSION,
        "manuscript": manuscript,
        "units": new_units,
    }
