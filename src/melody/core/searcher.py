"""
Cari YouTube dari CLI tanpa buka browser.
"""
from dataclasses import dataclass, field

import yt_dlp

from melody.utils.validators import normalize_yt_url


@dataclass
class SearchResult:
    index: int
    video_id: str
    title: str
    channel: str
    duration_str: str
    url: str
    # Indikasi kemungkinan DRM berdasarkan metadata (heuristik, tidak 100%)
    likely_drm: bool = field(default=False)


# Channel resmi label rekaman yang sering pakai DRM di YouTube Music
_DRM_CHANNEL_HINTS = {
    "youtube music", "vevo", "sony music", "universal music",
    "warner music", "warner records", "atlantic records", "republic records",
    "capitol records", "interscope records", "def jam",
}


def _fmt_duration(seconds: int | None) -> str:
    if not seconds:
        return "--:--"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02}:{s:02}"
    return f"{m}:{s:02}"


def _is_likely_drm(entry: dict) -> bool:
    """
    Heuristik ringan untuk deteksi kemungkinan DRM.
    Tidak 100% akurat — hanya sebagai indikasi awal di UI.
    URL search result sudah di-normalize ke youtube.com sebelum ini dipanggil,
    jadi cek berdasarkan channel saja.
    """
    channel = (entry.get("channel") or entry.get("uploader") or "").lower()
    for hint in _DRM_CHANNEL_HINTS:
        if hint in channel:
            return True
    return False


def search_youtube(query: str, max_results: int = 10) -> list[SearchResult]:
    """
    Cari YouTube dengan ytsearch, kembalikan list SearchResult.
    Tidak melakukan download sama sekali.
    Hasil diurutkan: non-DRM duluan.
    """
    # Minta lebih banyak dari yang diminta supaya ada buffer setelah filter
    fetch = max(max_results + 5, 15)
    search_url = f"ytsearch{fetch}:{query}"

    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
    }

    raw: list[SearchResult] = []

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(search_url, download=False)

    if not info or "entries" not in info:
        return raw

    for entry in info["entries"]:
        if not entry:
            continue
        vid_id = entry.get("id", "")
        raw_url = entry.get("url") or f"https://www.youtube.com/watch?v={vid_id}"
        url, _ = normalize_yt_url(raw_url)
        raw.append(
            SearchResult(
                index=0,          # di-assign ulang setelah sort
                video_id=vid_id,
                title=entry.get("title", "Unknown"),
                channel=entry.get("channel") or entry.get("uploader", "Unknown"),
                duration_str=_fmt_duration(entry.get("duration")),
                url=url,
                likely_drm=_is_likely_drm(entry),
            )
        )

    # Non-DRM duluan, DRM di bawah
    raw.sort(key=lambda r: r.likely_drm)

    # Assign ulang nomor urut dan potong sesuai max_results
    results = []
    for i, r in enumerate(raw[:max_results], 1):
        r.index = i
        results.append(r)

    return results
