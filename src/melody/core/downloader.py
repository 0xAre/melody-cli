"""
Semua interaksi dengan yt-dlp ada di sini.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yt_dlp

from melody.services import config_service, history_service, progress_service
from melody.utils.validators import extract_video_id


@dataclass
class DownloadResult:
    success: bool
    video_id: str = ""
    title: str = ""
    url: str = ""
    output_path: str = ""
    quality: str = ""
    skipped: bool = False
    error: str = ""


@dataclass
class DownloadSummary:
    ok: int = 0
    skipped: int = 0
    failed: int = 0
    results: list[DownloadResult] = field(default_factory=list)


def _build_ydl_opts(output_dir: Path, quality: str, hooks: list) -> dict[str, Any]:
    cfg = config_service.get_all()
    sample_rate = cfg.get("sample_rate", "44100")
    cookies_browser = cfg.get("cookies_browser", "")

    opts: dict[str, Any] = {
        # iOS client: paling stabil, jarang kena 403 dari YouTube
        "extractor_args": {
            "youtube": {
                "player_client": ["ios", "web"],
            }
        },
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            },
            {"key": "FFmpegMetadata", "add_metadata": True},
        ],
        "postprocessor_args": {
            "ffmpegextractaudio": [
                "-ar", sample_rate,
                "-ac", "2",
                "-codec:a", "libmp3lame",
            ]
        },
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "concurrent_fragment_downloads": 4,
        "retries": 10,
        "fragment_retries": 10,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                "Mobile/15E148 Safari/604.1"
            ),
        },
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,
        "progress_hooks": hooks,
    }

    # Kalau user set cookies_browser di config, pakai cookies dari browser tsb
    if cookies_browser:
        opts["cookiesfrombrowser"] = (cookies_browser, None, None, None)

    return opts


def download_one(
    url: str,
    output_dir: Path,
    quality: str,
    skip_history: bool = True,
    show_progress: bool = True,
) -> DownloadResult:
    """Download satu URL (video atau playlist item) → MP3."""

    video_id = extract_video_id(url) or url

    # Dedup check
    if skip_history and history_service.is_downloaded(video_id):
        return DownloadResult(
            success=True, video_id=video_id, url=url, skipped=True,
            title="(sudah ada di history)"
        )

    hooks: list = []
    progress = None
    task_id = None

    if show_progress:
        progress = progress_service.make_progress()
        progress.start()
        task_id = progress.add_task(f"[cyan]{url[:60]}[/cyan]", total=None)
        hooks.append(progress_service.make_ydl_hook(progress, task_id))

    opts = _build_ydl_opts(output_dir, quality, hooks)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)

        if info is None:
            return DownloadResult(success=False, url=url, error="Tidak ada info dari yt-dlp")

        # Playlist → ambil item pertama jika ada
        entry = info
        if "entries" in info and info["entries"]:
            entry = info["entries"][0] or info

        vid_id = entry.get("id", video_id)
        title = entry.get("title", "Unknown")
        ext = entry.get("ext", "mp3")
        safe_title = ydl.prepare_filename(entry).replace(f".{ext}", ".mp3")

        result = DownloadResult(
            success=True,
            video_id=vid_id,
            title=title,
            url=url,
            output_path=safe_title,
            quality=quality,
        )

        history_service.record(
            history_service.DownloadRecord(
                video_id=vid_id, title=title, url=url,
                output_path=safe_title, quality=quality,
            )
        )

        if progress and task_id is not None:
            progress.update(task_id, description=f"[green]✓ {title[:50]}[/green]")

        return result

    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        # Terjemahkan error umum ke pesan yang lebih actionable
        if "403" in msg or "Forbidden" in msg:
            msg = (
                "HTTP 403 Forbidden — YouTube memblokir request.\n"
                "  Fix 1: jalankan  melody fix-403  untuk coba otomatis\n"
                "  Fix 2: set cookies browser via  melody config show --set cookies_browser=chrome"
            )
        elif "Sign in" in msg or "bot" in msg.lower():
            msg = (
                "YouTube meminta login / mendeteksi bot.\n"
                "  Fix: melody config show --set cookies_browser=chrome  (atau firefox/edge)"
            )
        if progress and task_id is not None:
            progress.update(task_id, description=f"[red]✗ Error[/red]")
        return DownloadResult(success=False, url=url, error=msg)

    except Exception as e:
        return DownloadResult(success=False, url=url, error=str(e))

    finally:
        if progress:
            progress.stop()


def download_playlist(
    url: str,
    output_dir: Path,
    quality: str,
    skip_history: bool = True,
) -> DownloadSummary:
    """Download seluruh playlist. Tiap item tampil progress bar sendiri."""
    summary = DownloadSummary()

    # Extract info dulu tanpa download untuk tahu jumlah item
    quiet_opts = {"quiet": True, "no_warnings": True, "extract_flat": "in_playlist"}
    with yt_dlp.YoutubeDL(quiet_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if info is None:
        summary.failed += 1
        return summary

    if "entries" not in info:
        # Bukan playlist, langsung download single
        r = download_one(url, output_dir, quality, skip_history)
        summary.results.append(r)
        if r.skipped:
            summary.skipped += 1
        elif r.success:
            summary.ok += 1
        else:
            summary.failed += 1
        return summary

    entries = [e for e in info["entries"] if e]
    total = len(entries)

    for i, entry in enumerate(entries, 1):
        entry_url = entry.get("url") or entry.get("webpage_url") or f"https://www.youtube.com/watch?v={entry['id']}"
        print(f"  [{i}/{total}] {entry.get('title', entry_url[:60])}")

        r = download_one(entry_url, output_dir, quality, skip_history)
        summary.results.append(r)
        if r.skipped:
            summary.skipped += 1
        elif r.success:
            summary.ok += 1
        else:
            summary.failed += 1

    return summary
