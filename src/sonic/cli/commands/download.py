from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from sonic.core.downloader import download_one, download_playlist
from sonic.services import config_service
from sonic.utils.ffmpeg import require_ffmpeg
from sonic.utils.validators import resolve_output_dir, validate_quality

app = typer.Typer(help="Download YouTube audio ke MP3")
console = Console()


def _run_download(urls: list[str], output_dir: Path, quality: str, no_skip: bool) -> None:
    require_ffmpeg()
    cfg = config_service.get_all()
    skip = cfg.get("skip_history", True) and not no_skip

    ok = skipped = failed = 0

    for url in urls:
        url = url.strip()
        if not url:
            continue

        console.print(f"\n[bold cyan]↓[/bold cyan] {url}")

        # Deteksi playlist vs single
        is_playlist = "playlist" in url or "list=" in url
        if is_playlist:
            s = download_playlist(url, output_dir, quality, skip_history=skip)
            ok += s.ok
            skipped += s.skipped
            failed += s.failed
        else:
            r = download_one(url, output_dir, quality, skip_history=skip)
            if r.skipped:
                console.print(f"  [yellow]⊘ Dilewati — sudah ada di history[/yellow]")
                skipped += 1
            elif r.success:
                console.print(f"  [green]✓ {r.title}[/green]")
                ok += 1
            else:
                console.print(f"  [red]✗ {r.error[:100]}[/red]")
                failed += 1

    console.print()
    _print_summary(ok, skipped, failed, str(output_dir))


def _print_summary(ok: int, skipped: int, failed: int, out: str) -> None:
    t = Table.grid(padding=(0, 2))
    t.add_row("[bold green]Berhasil[/bold green]", str(ok))
    t.add_row("[yellow]Dilewati[/yellow]", str(skipped))
    t.add_row("[red]Gagal[/red]", str(failed))
    t.add_row("[dim]Lokasi[/dim]", out)
    console.print(t)


@app.command("url")
def cmd_url(
    urls: Annotated[list[str], typer.Argument(help="Satu atau beberapa URL YouTube")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Folder output")] = None,
    quality: Annotated[str, typer.Option("--quality", "-q", help="Bitrate kbps: 128|192|256|320")] = "",
    no_skip: Annotated[bool, typer.Option("--no-skip", help="Paksa download meski sudah ada di history")] = False,
) -> None:
    """Download satu atau beberapa URL YouTube ke MP3."""
    cfg = config_service.get_all()
    q = quality or cfg.get("quality", "192")
    try:
        validate_quality(q)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    out_dir = resolve_output_dir(output, Path(cfg.get("output_dir", "~/Music")).expanduser())
    _run_download(list(urls), out_dir, q, no_skip)


@app.command("batch")
def cmd_batch(
    file: Annotated[Path, typer.Argument(help="File .txt berisi URL (satu per baris)")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o")] = None,
    quality: Annotated[str, typer.Option("--quality", "-q")] = "",
    no_skip: Annotated[bool, typer.Option("--no-skip")] = False,
) -> None:
    """Download banyak URL dari file teks."""
    if not file.exists():
        console.print(f"[red]File tidak ditemukan: {file}[/red]")
        raise typer.Exit(1)

    urls = [line.strip() for line in file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]

    if not urls:
        console.print("[yellow]File kosong atau tidak ada URL valid[/yellow]")
        raise typer.Exit(0)

    console.print(f"[cyan]{len(urls)} URL ditemukan di {file.name}[/cyan]")

    cfg = config_service.get_all()
    q = quality or cfg.get("quality", "192")
    try:
        validate_quality(q)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    out_dir = resolve_output_dir(output, Path(cfg.get("output_dir", "~/Music")).expanduser())
    _run_download(urls, out_dir, q, no_skip)
