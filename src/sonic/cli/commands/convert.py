from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from sonic.core.converter import SUPPORTED_EXTS, ConvertResult, convert_file, find_audio_files
from sonic.services import config_service
from sonic.utils.ffmpeg import require_ffmpeg
from sonic.utils.validators import validate_quality

app = typer.Typer(help="Konversi file audio lokal ke MP3")
console = Console()


@app.command("file")
def cmd_convert(
    inputs: Annotated[list[Path], typer.Argument(help="File atau folder yang akan dikonversi")],
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Folder output")] = None,
    quality: Annotated[str, typer.Option("--quality", "-q")] = "",
    overwrite: Annotated[bool, typer.Option("--overwrite", help="Timpa file yang sudah ada")] = False,
) -> None:
    """Konversi file WebM / M4A / WAV / FLAC / dll ke MP3."""
    require_ffmpeg()

    cfg = config_service.get_all()
    q = quality or cfg.get("quality", "192")
    try:
        validate_quality(q)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Kumpulkan semua file yang perlu diproses
    to_convert: list[Path] = []
    for inp in inputs:
        if inp.is_dir():
            found = find_audio_files(inp)
            if not found:
                console.print(f"[yellow]Tidak ada file audio di {inp}[/yellow]")
            to_convert.extend(found)
        elif inp.is_file():
            if inp.suffix.lower() in SUPPORTED_EXTS:
                to_convert.append(inp)
            else:
                console.print(f"[yellow]Format tidak didukung: {inp.name}[/yellow]")
        else:
            console.print(f"[red]Tidak ditemukan: {inp}[/red]")

    if not to_convert:
        console.print("[yellow]Tidak ada file yang diproses[/yellow]")
        raise typer.Exit(0)

    console.print(f"\n[cyan]{len(to_convert)} file ditemukan — kualitas {q} kbps[/cyan]\n")

    results: list[ConvertResult] = []
    sample_rate = cfg.get("sample_rate", "44100")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("Mengkonversi...", total=len(to_convert))

        for f in to_convert:
            out_dir = output or f.parent
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / (f.stem + ".mp3")

            progress.update(task, description=f"[cyan]{f.name[:50]}[/cyan]")
            r = convert_file(f, out_path, q, sample_rate, overwrite)
            results.append(r)
            progress.advance(task)

    # Ringkasan
    ok = [r for r in results if r.success]
    fail = [r for r in results if not r.success]

    console.print()
    t = Table(title="Hasil Konversi", show_header=True, header_style="bold cyan")
    t.add_column("File")
    t.add_column("Status")
    t.add_column("Ukuran")
    for r in results:
        name = Path(r.input_path).name
        if r.success:
            t.add_row(name, "[green]✓ OK[/green]", f"{r.size_mb} MB")
        else:
            t.add_row(name, "[red]✗ Gagal[/red]", r.error[:60])
    console.print(t)

    console.print(f"\n[green]Berhasil: {len(ok)}[/green]  [red]Gagal: {len(fail)}[/red]")
