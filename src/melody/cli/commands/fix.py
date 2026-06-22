"""
melody fix-403 — diagnosa dan perbaiki error 403 dari YouTube.
"""
import subprocess
import sys

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="Perbaiki error 403 / bot detection dari YouTube")
console = Console()


@app.command("403")
def cmd_fix_403() -> None:
    """Update yt-dlp ke versi terbaru dan test koneksi YouTube."""

    console.print(Panel(
        "[bold]Diagnosa error 403 / Forbidden[/bold]\n\n"
        "Penyebab paling umum:\n"
        "  1. yt-dlp outdated (YouTube rutin ganti format)\n"
        "  2. YouTube mendeteksi bot — perlu cookies browser\n"
        "  3. Video region-locked atau age-restricted",
        border_style="yellow",
        title="[yellow]melody fix-403[/yellow]",
    ))

    # Step 1: Update yt-dlp
    console.print("\n[cyan][1/3][/cyan] Update yt-dlp ke versi terbaru...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp", "--quiet"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            # Cek versi setelah update
            ver = subprocess.run(
                [sys.executable, "-m", "yt_dlp", "--version"],
                capture_output=True, text=True
            )
            console.print(f"  [green]✓[/green] yt-dlp {ver.stdout.strip()}")
        else:
            console.print(f"  [yellow]⚠[/yellow] Gagal update: {result.stderr.strip()[:100]}")
    except Exception as e:
        console.print(f"  [red]✗[/red] {e}")

    # Step 2: Test ekstrak info (tanpa download)
    console.print("\n[cyan][2/3][/cyan] Test koneksi ke YouTube...")
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    try:
        import yt_dlp
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
        if info:
            console.print(f"  [green]✓[/green] Koneksi OK — '{info.get('title', '?')}'")
        else:
            console.print("  [yellow]⚠[/yellow] Info kosong")
    except Exception as e:
        msg = str(e)
        if "403" in msg or "Forbidden" in msg:
            console.print("  [red]✗[/red] Masih 403 — perlu cookies browser")
            _show_cookies_guide()
        else:
            console.print(f"  [red]✗[/red] {msg[:120]}")
        return

    # Step 3: Panduan cookies (opsional)
    console.print("\n[cyan][3/3][/cyan] Koneksi berhasil tanpa cookies.")
    console.print(
        "\n[dim]Jika nanti muncul 403 lagi (biasanya video age-restricted),\n"
        "jalankan:[/dim]\n"
        "  [bold]melody config show --set cookies_browser=chrome[/bold]\n"
        "[dim]Ganti[/dim] chrome [dim]dengan browser yang kamu pakai (firefox / edge / brave)[/dim]"
    )


def _show_cookies_guide() -> None:
    console.print(Panel(
        "[bold]Cara pakai cookies browser:[/bold]\n\n"
        "Pastikan kamu sudah login YouTube di browser, lalu jalankan:\n\n"
        "  [bold cyan]melody config show --set cookies_browser=chrome[/bold cyan]\n\n"
        "Browser yang didukung:\n"
        "  chrome, firefox, edge, brave, opera, safari\n\n"
        "[dim]melody akan otomatis ambil cookies dari browser tersebut\n"
        "setiap kali download.[/dim]",
        border_style="cyan",
        title="[cyan]Cookies Browser[/cyan]",
    ))
