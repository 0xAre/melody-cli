import re
from pathlib import Path

VALID_QUALITIES = {"128", "192", "256", "320"}

# Cocokkan youtube.com/watch?v=ID, youtu.be/ID, shorts/, embed/
_YT_ID_RE = re.compile(
    r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})"
)

# Playlist: list=PL...
_YT_PLAYLIST_RE = re.compile(r"[?&]list=([A-Za-z0-9_-]+)")


def extract_video_id(url: str) -> str | None:
    """Kembalikan YouTube video ID dari URL, atau None jika tidak ditemukan."""
    m = _YT_ID_RE.search(url)
    return m.group(1) if m else None


def normalize_yt_url(url: str) -> tuple[str, bool]:
    """
    Normalisasi URL YouTube / YouTube Music ke format standar youtube.com.
    Return (normalized_url, was_converted).

    Contoh:
      music.youtube.com/watch?v=ABC  →  youtube.com/watch?v=ABC  (True)
      youtu.be/ABC                   →  youtube.com/watch?v=ABC  (True)
      youtube.com/watch?v=ABC        →  tidak berubah             (False)
      music.youtube.com/playlist?list=PL...  →  youtube.com/playlist?list=PL...
    """
    url = url.strip()

    # YouTube Music playlist
    if "music.youtube.com/playlist" in url or "music.youtube.com/browse" in url:
        pl_match = _YT_PLAYLIST_RE.search(url)
        if pl_match:
            return f"https://www.youtube.com/playlist?list={pl_match.group(1)}", True

    # YouTube Music video  →  YouTube video
    if "music.youtube.com" in url:
        vid_id = extract_video_id(url)
        if vid_id:
            return f"https://www.youtube.com/watch?v={vid_id}", True

    # youtu.be/ID  →  youtube.com/watch?v=ID
    if "youtu.be/" in url:
        vid_id = extract_video_id(url)
        if vid_id:
            return f"https://www.youtube.com/watch?v={vid_id}", True

    return url, False


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
