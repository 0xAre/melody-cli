from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from melody.services import config_service

app = typer.Typer(help="Kelola konfigurasi melody")
console = Console()


@app.command("show")
def cmd_config(
    show: Annotated[bool, typer.Option("--show", help="Tampilkan config aktif")] = False,
    set_: Annotated[Optional[str], typer.Option("--set", help="Set nilai: key=value")] = None,
    reset: Annotated[bool, typer.Option("--reset", help="Reset ke default")] = False,
) -> None:
    """
    Kelola config melody.

    \b
    Contoh:
      melody config --show
      melody config --set quality=320
      melody config --set output_dir=D:/Musik
      melody config --reset
    """
    if reset:
        config_service.reset()
        console.print("[yellow]Config direset ke default[/yellow]")
        return

    if set_:
        if "=" not in set_:
            console.print("[red]Format salah. Gunakan: --set key=value[/red]")
            raise typer.Exit(1)
        key, _, value = set_.partition("=")
        try:
            config_service.set_value(key.strip(), value.strip())
            console.print(f"[green]✓ {key} = {value}[/green]")
        except KeyError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(1)
        return

    # Default: --show
    cfg = config_service.get_all()
    defaults = config_service.DEFAULTS

    t = Table(show_header=True, header_style="bold cyan", border_style="dim", title="Konfigurasi Sonic")
    t.add_column("Key")
    t.add_column("Nilai Aktif")
    t.add_column("Default", style="dim")

    for key, default_val in defaults.items():
        current = cfg.get(key, default_val)
        changed = str(current) != str(default_val)
        style = "bold green" if changed else ""
        t.add_row(key, f"[{style}]{current}[/{style}]" if changed else str(current), str(default_val))

    console.print(t)
    console.print(f"\n[dim]File config: {config_service.config_path()}[/dim]")
