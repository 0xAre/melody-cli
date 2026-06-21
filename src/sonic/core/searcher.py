"""
Cari YouTube dari CLI tanpa buka browser.
"""
from dataclasses import dataclass

import yt_dlp


@dataclass
class SearchResult:
    index: int
    video_id: str
    title: str
    channel: str
    duration_str: str
    url: str


def _fmt_duration(seconds: int | None) -> str:
    if not seconds:
        return "--:--"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02}:{s:02}"
    return f"{m}:{s:02}"


def search_youtube(query: str, max_results: int = 10) -> list[SearchResult]:
    """
    Cari YouTube dengan ytsearch, kembalikan list SearchResult.
    Tidak melakukan download sama sekali.
    """
    search_url = f"ytsearch{max_results}:{query}"

    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
    }

    results: list[SearchResult] = []

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(search_url, download=False)

    if not info or "entries" not in info:
        return results

    for i, entry in enumerate(info["entries"], 1):
        if not entry:
            continue
        vid_id = entry.get("id", "")
        results.append(
            SearchResult(
                index=i,
                video_id=vid_id,
                title=entry.get("title", "Unknown"),
                channel=entry.get("channel") or entry.get("uploader", "Unknown"),
                duration_str=_fmt_duration(entry.get("duration")),
                url=entry.get("url") or f"https://www.youtube.com/watch?v={vid_id}",
            )
        )

    return results
