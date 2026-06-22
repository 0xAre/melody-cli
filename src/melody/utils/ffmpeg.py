import shutil
import subprocess
import sys

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()


def _try_static_ffmpeg() -> bool:
    """Coba pakai static-ffmpeg sebagai fallback. Return True jika berhasil."""
    try:
        import static_ffmpeg
    except ImportError:
        return False

    console.print(
        "\n  [yellow]FFmpeg tidak ditemukan di sistem.[/yellow]\n"
        "  [dim]Mengunduh FFmpeg otomatis (sekali saja, ~80 MB)...[/dim]\n"
    )
    try:
        static_ffmpeg.add_paths()
        return bool(shutil.which("ffmpeg"))
    except Exception:
        return False


def require_ffmpeg() -> None:
    """Cek FFmpeg tersedia. Fallback ke static-ffmpeg jika tidak ada di PATH."""
    if shutil.which("ffmpeg"):
        return

    if _try_static_ffmpeg():
        console.print("  [green]FFmpeg siap.[/green]\n")
        return

    # Tidak ada system FFmpeg dan static-ffmpeg gagal — tampilkan panduan manual
    guide = {
        "win32": (
            "[bold]Windows[/bold]\n"
            "  winget install -e --id Gyan.FFmpeg\n"
            "  [dim]atau[/dim] choco install ffmpeg"
        ),
        "darwin": "[bold]macOS[/bold]\n  brew install ffmpeg",
        "linux": (
            "[bold]Linux[/bold]\n"
            "  sudo apt install ffmpeg   [dim](Debian/Ubuntu)[/dim]\n"
            "  sudo dnf install ffmpeg   [dim](Fedora)[/dim]\n"
            "  sudo pacman -S ffmpeg     [dim](Arch)[/dim]"
        ),
    }.get(sys.platform, "sudo apt install ffmpeg")

    console.print(
        Panel(
            "[red bold]FFmpeg tidak ditemukan![/red bold]\n\n"
            "melody membutuhkan FFmpeg untuk konversi audio.\n\n"
            f"{guide}\n\n"
            "[dim]Atau install ulang melody agar static-ffmpeg ikut terpasang:[/dim]\n"
            "  pip install melody-mp3[ffmpeg]",
            title="[red]Error[/red]",
            border_style="red",
        )
    )
    raise typer.Exit(1)


def ffmpeg_version() -> str:
    """Return string versi FFmpeg singkat."""
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        line = r.stdout.split("\n")[0]
        # "ffmpeg version 6.1.1 ..." → "6.1.1"
        parts = line.split()
        if len(parts) >= 3:
            return parts[2]
    except Exception:
        pass
    return "unknown"
