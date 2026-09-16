import re


VALID_RULE_TYPES = {"rewrite", "ipa"}


def validate_pronunciation(pronunciation: dict) -> None:
    if not isinstance(pronunciation, dict):
        raise TypeError("pronunciation must be a dictionary")

    for source, rule in pronunciation.items():
        if not isinstance(source, str) or not source:
            raise ValueError("pronunciation source must be a non-empty string")

        if not isinstance(rule, dict):
            raise ValueError(
                f"pronunciation rule for {source!r} must be a dictionary"
            )

        rule_type = rule.get("type")
        value = rule.get("value")

        if rule_type not in VALID_RULE_TYPES:
            raise ValueError(
                f"unknown pronunciation rule type for {source!r}: "
                f"{rule_type!r}"
            )

        if not isinstance(value, str) or not value:
            raise ValueError(
                f"pronunciation value for {source!r} "
                "must be a non-empty string"
            )


def apply_pronunciation(
    text: str,
    pronunciation: dict,
) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    validate_pronunciation(pronunciation)

    rendered = text

    # Longest source first prevents a shorter rule from consuming
    # part of a longer known expression.
    rules = sorted(
        pronunciation.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for source, rule in rules:
        rule_type = rule["type"]
        value = rule["value"]

        if rule_type == "ipa":
            replacement = f"[[ {value} ]]"
        else:
            replacement = value

        pattern = re.compile(
            rf"(?<!\w){re.escape(source)}(?!\w)"
        )

        rendered = pattern.sub(
            lambda _match, replacement=replacement: replacement,
            rendered,
        )

    return rendered
