from hashlib import sha256


def render_fingerprint(
    *,
    render_text: str,
    voice_id: str,
) -> str:
    if not isinstance(render_text, str):
        raise TypeError("render_text must be a string")

    if not isinstance(voice_id, str):
        raise TypeError("voice_id must be a string")

    payload = (
        f"renderText:{render_text}\n"
        f"voiceId:{voice_id}"
    ).encode("utf-8")

    return sha256(payload).hexdigest()


def audio_state(
    *,
    rendered_fingerprint: str | None,
    render_text: str,
    voice_id: str,
) -> str:
    if rendered_fingerprint is None:
        return "idle"

    current_fingerprint = render_fingerprint(
        render_text=render_text,
        voice_id=voice_id,
    )

    if rendered_fingerprint == current_fingerprint:
        return "ready"

    return "stale"


def begin_render(
    *,
    rendered_fingerprint: str | None,
) -> dict:
    return {
        "status": "rendering",
        "renderedFingerprint": rendered_fingerprint,
    }


def complete_render(
    *,
    render_text: str,
    voice_id: str,
) -> dict:
    return {
        "status": "ready",
        "renderedFingerprint": render_fingerprint(
            render_text=render_text,
            voice_id=voice_id,
        ),
    }


def fail_render(
    *,
    rendered_fingerprint: str | None,
    error: str,
) -> dict:
    return {
        "status": "error",
        "renderedFingerprint": rendered_fingerprint,
        "error": error,
    }
