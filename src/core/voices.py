def validate_voices(voices: dict) -> None:
    if not isinstance(voices, dict):
        raise TypeError("voices must be a dictionary")

    if not voices:
        raise ValueError("voice registry must not be empty")

    defaults = []

    for voice_id, voice in voices.items():
        if not isinstance(voice_id, str) or not voice_id:
            raise ValueError("voice ID must be a non-empty string")

        if not isinstance(voice, dict):
            raise ValueError(
                f"voice {voice_id!r} must be a dictionary"
            )

        name = voice.get("name")
        role = voice.get("role")
        model_ref = voice.get("modelRef")

        if not isinstance(name, str) or not name:
            raise ValueError(
                f"voice {voice_id!r} requires a name"
            )

        if not isinstance(role, str) or not role:
            raise ValueError(
                f"voice {voice_id!r} requires a role"
            )

        if not isinstance(model_ref, str) or not model_ref:
            raise ValueError(
                f"voice {voice_id!r} requires a modelRef"
            )

        if role == "default":
            defaults.append(voice_id)

    if len(defaults) != 1:
        raise ValueError(
            "voice registry must contain exactly one default voice"
        )


def get_default_voice_id(voices: dict) -> str:
    validate_voices(voices)

    return next(
        voice_id
        for voice_id, voice in voices.items()
        if voice["role"] == "default"
    )


def require_voice(voices: dict, voice_id: str) -> dict:
    validate_voices(voices)

    if voice_id not in voices:
        raise ValueError(
            f"unknown voice ID: {voice_id!r}"
        )

    return voices[voice_id]
