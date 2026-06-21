import typer
from rich.console import Console

from sonic import __version__
from sonic.cli.commands import config, convert, download, history, search

app = typer.Typer(
    name="sonic",
    help="sonic — YouTube to MP3 downloader yang cepat & elegan.",
    no_args_is_help=False,       # tanpa args → interactive wizard
    rich_markup_mode="rich",
    add_completion=True,
)

console = Console()

# ── Subcommands ────────────────────────────────────────────────
app.add_typer(download.app, name="download", help="Download YouTube URL ke MP3")
app.add_typer(convert.app,  name="convert",  help="Konversi file audio lokal ke MP3")
app.add_typer(search.app,   name="search",   help="Cari YouTube dan download")
app.add_typer(history.app,  name="history",  help="Riwayat download")
app.add_typer(config.app,   name="config",   help="Konfigurasi sonic")


# ── Shortcut: sonic get <url> ──────────────────────────────────
@app.command("get", hidden=True)
def cmd_get(
    url: str = typer.Argument(..., help="URL YouTube"),
    output: str = typer.Option("", "--output", "-o"),
    quality: str = typer.Option("", "--quality", "-q"),
) -> None:
    """Shortcut: sonic get <url>  (sama dengan sonic download url <url>)"""
    from pathlib import Path

    from sonic.core.downloader import download_one, download_playlist
    from sonic.services import config_service
    from sonic.utils.ffmpeg import require_ffmpeg
    from sonic.utils.validators import resolve_output_dir, validate_quality

    require_ffmpeg()
    cfg = config_service.get_all()
    q = quality or cfg.get("quality", "192")
    try:
        validate_quality(q)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    out_dir = resolve_output_dir(
        output or None,
        Path(cfg.get("output_dir", "~/Music")).expanduser(),
    )

    if "playlist" in url or "list=" in url:
        s = download_playlist(url, out_dir, q)
        console.print(
            f"[green]Berhasil: {s.ok}[/green]  "
            f"[yellow]Skip: {s.skipped}[/yellow]  "
            f"[red]Gagal: {s.failed}[/red]"
        )
    else:
        r = download_one(url, out_dir, q)
        if r.skipped:
            console.print("[yellow]⊘ Sudah ada di history[/yellow]")
        elif r.success:
            console.print(f"[green]✓ {r.title}[/green]  →  {out_dir}")
        else:
            console.print(f"[red]✗ {r.error[:150]}[/red]")
            raise typer.Exit(1)


# ── Version flag ───────────────────────────────────────────────
def _version_cb(value: bool) -> None:
    if value:
        console.print(f"sonic [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()


# ── Root callback — launch wizard jika tidak ada subcommand ────
@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        None, "--version", "-V",
        callback=_version_cb, is_eager=True,
        help="Tampilkan versi",
    ),
) -> None:
    if ctx.invoked_subcommand is None:
        from sonic.cli.interactive import run_interactive
        run_interactive()


def main() -> None:
    app()
