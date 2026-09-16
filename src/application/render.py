from src.core.render_units import build_render_units


def render_manuscript(
    *,
    manuscript: str,
    pronunciation: dict,
    voices: dict,
    runtime,
    voice_plan: dict | None = None,
) -> list[dict]:
    units = build_render_units(
        manuscript=manuscript,
        pronunciation=pronunciation,
        voices=voices,
        voice_plan=voice_plan,
    )

    results = []

    for unit in units:
        audio_path = runtime.render(unit)

        results.append(
            {
                "unitId": unit["id"],
                "audioPath": audio_path,
            }
        )

    return results
