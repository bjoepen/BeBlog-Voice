import re


def split_paragraphs(manuscript: str) -> list[str]:
    """
    Split a manuscript into non-empty paragraphs.

    A paragraph is separated by one or more blank lines.
    The manuscript itself is never modified.
    """
    if not isinstance(manuscript, str):
        raise TypeError("manuscript must be a string")

    return [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", manuscript)
        if paragraph.strip()
    ]
