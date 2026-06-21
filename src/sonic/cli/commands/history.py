from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from sonic.services import history_service

app = typer.Typer(help="Lihat dan kelola riwayat download")
console = Console()


@app.command("show")
def cmd_history(
    last: Annotated[int, typer.Option("--last", "-n", help="Tampilkan N entri terakhir")] = 20,
    clear: Annotated[bool, typer.Option("--clear", help="Hapus semua history")] = False,
    find: Annotated[str, typer.Option("--find", "-f", help="Filter berdasarkan judul")] = "",
) -> None:
    """Tampilkan riwayat download MP3."""
    if clear:
        n = history_service.clear()
        console.print(f"[yellow]History dihapus ({n} entri)[/yellow]")
        return

    rows = history_service.get_recent(last)

    if find:
        rows = [r for r in rows if find.lower() in r["title"].lower()]

    if not rows:
        console.print("[dim]Belum ada history download[/dim]")
        console.print(f"[dim]Database: {history_service.db_path()}[/dim]")
        return

    t = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        title=f"Riwayat Download — {len(rows)} entri",
    )
    t.add_column("#", width=4, justify="right")
    t.add_column("Judul", min_width=30)
    t.add_column("Kualitas", width=8, justify="center")
    t.add_column("Tanggal", width=20, style="dim")

    for i, row in enumerate(rows, 1):
        date = row["downloaded_at"][:19].replace("T", " ") if row.get("downloaded_at") else "-"
        t.add_row(str(i), row["title"], f"{row['quality']} kbps", date)

    console.print(t)
    console.print(f"\n[dim]Database: {history_service.db_path()}[/dim]")
