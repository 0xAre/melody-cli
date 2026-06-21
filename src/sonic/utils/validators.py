import re
from pathlib import Path

VALID_QUALITIES = {"128", "192", "256", "320"}

# Cocokkan youtube.com/watch?v=ID dan youtu.be/ID
_YT_ID_RE = re.compile(
    r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})"
)


def extract_video_id(url: str) -> str | None:
    """Kembalikan YouTube video ID dari URL, atau None jika bukan YouTube."""
    m = _YT_ID_RE.search(url)
    return m.group(1) if m else None


def validate_quality(value: str) -> str:
    """Pastikan nilai kualitas valid, raise ValueError kalau tidak."""
    if value not in VALID_QUALITIES:
        raise ValueError(
            f"Kualitas '{value}' tidak valid. Pilih: {', '.join(sorted(VALID_QUALITIES))} kbps"
        )
    return value


def resolve_output_dir(path: str | Path | None, default: Path) -> Path:
    """Resolve output directory: pakai path user jika ada, fallback ke default."""
    if path is None:
        target = default
    else:
        target = Path(path).expanduser()
    target.mkdir(parents=True, exist_ok=True)
    return target
