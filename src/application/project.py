from copy import deepcopy
from uuid import uuid4
from difflib import SequenceMatcher

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

    matcher = SequenceMatcher(
        a=old_paragraphs,
        b=new_paragraphs,
        autojunk=False,
    )

    new_units = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            new_units.extend(
                deepcopy(old_units[i1:i2])
            )
            continue

        if tag in {"insert", "replace"}:
            new_units.extend(
                _new_unit()
                for _paragraph
                in new_paragraphs[j1:j2]
            )

        # delete contributes no units

    return {
        "version": PROJECT_VERSION,
        "manuscript": manuscript,
        "units": new_units,
    }
