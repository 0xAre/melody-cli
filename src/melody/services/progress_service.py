"""
Factory untuk Rich Progress yang terintegrasi dengan yt-dlp progress hook.
"""
from typing import Callable

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)


def make_progress() -> Progress:
    """Return Progress instance dengan kolom yang cocok untuk download."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}[/bold cyan]", justify="left"),
        BarColumn(bar_width=30),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        transient=False,
    )


def make_ydl_hook(progress: Progress, task_id: TaskID) -> Callable[[dict], None]:
    """
    Kembalikan callable yang cocok dengan signature yt-dlp progress hook.
    Panggil ini sekali per task, inject ke ydl_opts['progress_hooks'].
    """
    def hook(d: dict) -> None:
        status = d.get("status")
        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0) or 0
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            if total > 0:
                progress.update(task_id, completed=downloaded, total=total)
            else:
                progress.update(task_id, advance=1024)
        elif status == "finished":
            total = d.get("total_bytes") or progress.tasks[task_id].total or 100
            progress.update(task_id, completed=total, total=total,
                            description="[green]Selesai — memproses...[/green]")
        elif status == "error":
            progress.update(task_id, description="[red]Error[/red]")

    return hook
