"""melody report — laporkan bug ke GitHub."""
import platform
import subprocess
import sys
import urllib.parse
import webbrowser

import typer
from rich.console import Console

from melody import __version__

app = typer.Typer(help="Laporkan bug ke GitHub")
console = Console()

_REPO = "0xAre/melody-cli"
_ISSUES_URL = f"https://github.com/{_REPO}/issues/new"


def _sysinfo() -> str:
    """Kumpulkan info sistem untuk bug report."""
    os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
    py_info = f"{sys.version.split()[0]}"
    try:
        ytdlp = subprocess.check_output(
            ["yt-dlp", "--version"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        ytdlp = "tidak ditemukan"
    return (
        f"**Versi melody:** {__version__}\n"
        f"**yt-dlp:** {ytdlp}\n"
        f"**Python:** {py_info}\n"
        f"**OS:** {os_info}\n"
    )


def open_report(title: str = "", description: str = "") -> None:
    """Buka GitHub issue page dengan info pre-filled."""
    info = _sysinfo()
    body = (
        "## Deskripsi\n"
        f"{description or '<!-- Jelaskan bug yang terjadi -->'}\n\n"
        "## Langkah reproduksi\n"
        "1. \n2. \n3. \n\n"
        "## Perilaku yang diharapkan\n"
        "<!-- Seharusnya seperti apa? -->\n\n"
        "## Info sistem\n"
        f"{info}"
    )
    params = urllib.parse.urlencode({
        "title": title or "[Bug] ",
        "body": body,
        "labels": "bug",
    })
    url = f"{_ISSUES_URL}?{params}"
    webbrowser.open(url)


@app.callback(invoke_without_command=True)
def cmd_report(
    title: str = typer.Option("", "--title", "-t", help="Judul singkat bug"),
) -> None:
    """Laporkan bug — buka GitHub issue dengan info sistem pre-filled."""
    console.print()
    console.print("  [bold cyan]Laporan Bug[/bold cyan]\n")
    console.print("  Info sistem berikut akan ditambahkan otomatis:\n")

    info = _sysinfo()
    for line in info.strip().splitlines():
        console.print(f"  [dim]{line}[/dim]")

    console.print()
    desc = typer.prompt("  Deskripsikan masalahnya (opsional)", default="")
    if not title:
        title = typer.prompt("  Judul singkat", default="[Bug] ")

    console.print()
    console.print("  [dim]Membuka browser ke GitHub Issues...[/dim]")
    open_report(title=title, description=desc)
    console.print("  [green]Browser terbuka.[/green] Lengkapi form lalu klik Submit.")
    console.print()
