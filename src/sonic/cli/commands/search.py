from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from sonic.core.downloader import download_one
from sonic.core.searcher import search_youtube
from sonic.services import config_service
from sonic.utils.ffmpeg import require_ffmpeg
from sonic.utils.validators import resolve_output_dir, validate_quality

app = typer.Typer(help="Cari lagu di YouTube dan langsung download")
console = Console()


@app.command("query")
def cmd_search(
    query: Annotated[str, typer.Argument(help="Judul atau kata kunci lagu")],
    results: Annotated[int, typer.Option("--results", "-n", help="Jumlah hasil pencarian")] = 10,
    download: Annotated[bool, typer.Option("--download", "-d", help="Pilih dan langsung download")] = False,
    output: Annotated[Optional[Path], typer.Option("--output", "-o")] = None,
    quality: Annotated[str, typer.Option("--quality", "-q")] = "",
) -> None:
    """Cari YouTube, tampilkan hasil, (opsional) langsung download."""
    console.print(f"\n[cyan]Mencari:[/cyan] {query}\n")

    hits = search_youtube(query, max_results=results)

    if not hits:
        console.print("[yellow]Tidak ada hasil ditemukan[/yellow]")
        raise typer.Exit(0)

    # Tabel hasil
    t = Table(show_header=True, header_style="bold cyan", border_style="dim")
    t.add_column("#", style="bold", width=3)
    t.add_column("Judul", min_width=30)
    t.add_column("Channel", style="dim", min_width=15)
    t.add_column("Durasi", justify="right", width=8)
    for h in hits:
        t.add_row(str(h.index), h.title, h.channel, h.duration_str)
    console.print(t)

    if not download:
        console.print("\n[dim]Tip: tambahkan --download untuk pilih dan langsung download[/dim]")
        return

    # Pilih nomor
    require_ffmpeg()
    raw = typer.prompt(f"\nPilih nomor (1-{len(hits)}, pisah koma untuk banyak)")
    chosen: list = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part)
            if 1 <= idx <= len(hits):
                chosen.append(hits[idx - 1])

    if not chosen:
        console.print("[yellow]Tidak ada pilihan valid[/yellow]")
        raise typer.Exit(0)

    cfg = config_service.get_all()
    q = quality or cfg.get("quality", "192")
    try:
        validate_quality(q)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    out_dir = resolve_output_dir(output, Path(cfg.get("output_dir", "~/Music")).expanduser())
    skip = cfg.get("skip_history", True)

    for item in chosen:
        console.print(f"\n[bold cyan]↓[/bold cyan] {item.title}")
        r = download_one(item.url, out_dir, q, skip_history=skip)
        if r.skipped:
            console.print(f"  [yellow]⊘ Sudah ada di history[/yellow]")
        elif r.success:
            console.print(f"  [green]✓ Tersimpan → {out_dir}[/green]")
        else:
            console.print(f"  [red]✗ {r.error[:100]}[/red]")
