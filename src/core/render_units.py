from src.core.manuscript import split_paragraphs
from src.core.pronunciation import apply_pronunciation
from src.core.voices import (
    get_default_voice_id,
    require_voice,
    validate_voices,
)


def build_render_units(
    manuscript: str,
    pronunciation: dict,
    voices: dict,
    voice_plan: dict | None = None,
) -> list[dict]:
    """
    Build deterministic render units from a manuscript.

    The manuscript remains untouched.
    Voice selection is production metadata.
    Render text is derived from the original paragraph text.
    """
    validate_voices(voices)

    if voice_plan is None:
        voice_plan = {}

    if not isinstance(voice_plan, dict):
        raise TypeError("voice_plan must be a dictionary")

    paragraphs = split_paragraphs(manuscript)
    default_voice_id = get_default_voice_id(voices)

    units = []

    for index, paragraph in enumerate(paragraphs, start=1):
        unit_id = f"{index:03d}"

        voice_id = voice_plan.get(
            unit_id,
            default_voice_id,
        )

        require_voice(voices, voice_id)

        units.append(
            {
                "id": unit_id,
                "originalText": paragraph,
                "renderText": apply_pronunciation(
                    paragraph,
                    pronunciation,
                ),
                "voiceId": voice_id,
            }
        )

    return units
