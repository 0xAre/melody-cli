import shutil
import subprocess
import sys

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

INSTALL_GUIDE = {
    "win32": (
        "[bold]Windows[/bold]\n"
        "  winget install -e --id Gyan.FFmpeg\n"
        "  [dim]atau[/dim] choco install ffmpeg\n"
        "  [dim]atau download manual:[/dim] https://ffmpeg.org/download.html"
    ),
    "darwin": (
        "[bold]macOS[/bold]\n"
        "  brew install ffmpeg"
    ),
    "linux": (
        "[bold]Linux[/bold]\n"
        "  sudo apt install ffmpeg        [dim](Debian/Ubuntu)[/dim]\n"
        "  sudo dnf install ffmpeg        [dim](Fedora)[/dim]\n"
        "  sudo pacman -S ffmpeg          [dim](Arch)[/dim]"
    ),
}


def require_ffmpeg() -> None:
    """Cek FFmpeg tersedia, exit dengan pesan jelas kalau tidak ada."""
    if shutil.which("ffmpeg"):
        return

    platform = sys.platform
    guide = INSTALL_GUIDE.get(platform, INSTALL_GUIDE["linux"])

    console.print(
        Panel(
            f"[red bold]FFmpeg tidak ditemukan![/red bold]\n\n"
            f"melody membutuhkan FFmpeg untuk konversi audio.\n\n"
            f"{guide}",
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
