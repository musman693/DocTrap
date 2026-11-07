import re
import unicodedata

ZERO_WIDTH = {"\u200b", "\u200c", "\u200d", "\ufeff"}
BIDI_CHARS = {"\u202a", "\u202b", "\u202c", "\u202d", "\u202e"}


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    # Remove common control chars that are often used to hide instructions.
    value = "".join(ch for ch in value if ch not in ZERO_WIDTH and ch not in BIDI_CHARS)
    value = value.replace("\x00", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def decode_tag_like_text(value: str) -> str:
    return value.replace("\u200b", "").replace("\u200c", "").replace("\u2066", "").replace("\u2069", "")
