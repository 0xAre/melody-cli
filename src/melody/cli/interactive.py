"""
Interactive wizard — default mode ketika `melody` dijalankan tanpa argumen.
Navigasi dengan arrow keys, tidak perlu hafal command apapun.
"""
import sys
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from melody import __version__
from melody.services import config_service

console = Console()

# ── Warna tema ──────────────────────────────────────────────────
THEME = questionary.Style([
    ("qmark",       "fg:#00d7af bold"),
    ("question",    "bold"),
    ("answer",      "fg:#00d7af bold"),
    ("pointer",     "fg:#00d7af bold"),
    ("highlighted", "fg:#00d7af bold"),
    ("selected",    "fg:#00d7af"),
    ("separator",   "fg:#555555"),
    ("instruction", "fg:#555555 italic"),
    ("text",        ""),
])

QUALITY_CHOICES = [
    questionary.Choice("192 kbps  —  bagus  (rekomendasi)",  value="192"),
    questionary.Choice("128 kbps  —  ringan, cocok flash drive", value="128"),
    questionary.Choice("256 kbps  —  sangat bagus",          value="256"),
    questionary.Choice("320 kbps  —  terbaik, file lebih besar", value="320"),
]


# ── Helpers ─────────────────────────────────────────────────────

def _q(result):
    """Return None kalau user Ctrl+C, else return result."""
    return result


def banner():
    console.print(Panel(
        f"[bold cyan]melody[/bold cyan]  [dim]v{__version__}[/dim]\n"
        "[dim]YouTube → MP3  •  Cari, Download, Konversi[/dim]",
        border_style="cyan",
        padding=(0, 3),
        width=44,
    ))


def _ask_quality(default: str = "192") -> str | None:
    # Pindah default ke posisi pertama
    choices = sorted(QUALITY_CHOICES, key=lambda c: (c.value != default, c.value))
    return questionary.select(
        "Kualitas MP3:", choices=choices, style=THEME,
        use_shortcuts=False,
    ).ask()


def _ask_output_dir(default: Path) -> Path | None:
    use_default = questionary.confirm(
        f"Simpan ke folder:  {default}",
        default=True,
        style=THEME,
    ).ask()

    if use_default is None:
        return None
    if use_default:
        return default

    raw = questionary.text(
        "Masukkan path folder tujuan:",
        style=THEME,
    ).ask()

    if not raw:
        return None

    p = Path(raw.strip()).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p


def _result_ok(title: str, out_dir: Path) -> None:
    console.print(f"  [green]✓[/green] [bold]{title}[/bold]")
    console.print(f"     [dim]→ {out_dir}[/dim]")


def _result_skip() -> None:
    console.print("  [yellow]⊘[/yellow] [dim]Sudah ada di history, dilewati[/dim]")


def _result_fail(err: str) -> None:
    console.print(f"  [red]✗[/red] {err[:120]}")


# ── Flows ───────────────────────────────────────────────────────

def flow_download() -> None:
    from melody.core.downloader import download_one, download_playlist
    from melody.utils.ffmpeg import require_ffmpeg

    require_ffmpeg()

    url = questionary.text(
        "URL YouTube  (lagu tunggal atau playlist):",
        style=THEME,
    ).ask()

    if not url or not url.strip():
        return
    url = url.strip()

    cfg = config_service.get_all()
    quality = _ask_quality(cfg.get("quality", "192"))
    if quality is None:
        return

    out_dir = _ask_output_dir(Path(cfg.get("output_dir", "~/Music")).expanduser())
    if out_dir is None:
        return

    console.print()
    skip = cfg.get("skip_history", True)
    is_playlist = "playlist" in url or "list=" in url

    if is_playlist:
        s = download_playlist(url, out_dir, quality, skip_history=skip)
        console.print(
            f"\n  [green]Berhasil: {s.ok}[/green]  "
            f"[yellow]Dilewati: {s.skipped}[/yellow]  "
            f"[red]Gagal: {s.failed}[/red]"
        )
        console.print(f"  [dim]Lokasi: {out_dir}[/dim]")
    else:
        r = download_one(url, out_dir, quality, skip_history=skip)
        if r.skipped:
            _result_skip()
        elif r.success:
            _result_ok(r.title, out_dir)
        else:
            _result_fail(r.error)


def flow_batch() -> None:
    from melody.core.downloader import download_one
    from melody.utils.ffmpeg import require_ffmpeg

    require_ffmpeg()

    raw = questionary.text(
        "Path ke file .txt berisi daftar URL:",
        style=THEME,
    ).ask()

    if not raw:
        return

    p = Path(raw.strip()).expanduser()
    if not p.exists():
        console.print(f"  [red]File tidak ditemukan:[/red] {p}")
        return

    urls = [
        line.strip()
        for line in p.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

    if not urls:
        console.print("  [yellow]File kosong atau tidak ada URL valid[/yellow]")
        return

    console.print(f"  [cyan]{len(urls)} URL ditemukan[/cyan]")

    cfg = config_service.get_all()
    quality = _ask_quality(cfg.get("quality", "192"))
    if quality is None:
        return

    out_dir = _ask_output_dir(Path(cfg.get("output_dir", "~/Music")).expanduser())
    if out_dir is None:
        return

    skip = cfg.get("skip_history", True)
    ok = skipped = failed = 0

    console.print()
    for i, url in enumerate(urls, 1):
        console.print(f"  [dim][{i}/{len(urls)}][/dim] {url[:65]}")
        r = download_one(url, out_dir, quality, skip_history=skip)
        if r.skipped:
            _result_skip()
            skipped += 1
        elif r.success:
            _result_ok(r.title, out_dir)
            ok += 1
        else:
            _result_fail(r.error)
            failed += 1

    console.print(
        f"\n  [green]Berhasil: {ok}[/green]  "
        f"[yellow]Dilewati: {skipped}[/yellow]  "
        f"[red]Gagal: {failed}[/red]"
    )


def _try_drm_fallback(failed_item, all_results: dict, selected: list, out_dir, quality, skip) -> None:
    """Kalau video DRM, coba video lain dari hasil search yang belum dipilih."""
    from melody.core.downloader import download_one

    selected_ids = {s.video_id for s in selected}
    candidates = [
        r for r in all_results.values()
        if r.video_id not in selected_ids and r.video_id != failed_item.video_id
    ]

    if not candidates:
        console.print("  [dim]Tidak ada alternatif di hasil search ini.[/dim]")
        console.print("  [dim]Tip: cari ulang dengan tambahkan 'lirik' atau 'official audio'[/dim]")
        return

    for alt in candidates:
        console.print(f"  [dim]  → mencoba:[/dim] {alt.title[:55]}")
        r = download_one(alt.url, out_dir, quality, skip_history=skip)
        if r.drm:
            console.print(f"  [yellow]  ⊘ DRM juga, skip...[/yellow]")
            continue
        if r.skipped:
            _result_skip()
            return
        if r.success:
            _result_ok(r.title, out_dir)
            return
        # Error lain, stop
        _result_fail(r.error)
        return

    console.print("  [yellow]Semua alternatif juga DRM protected.[/yellow]")
    console.print("  [dim]Tip: paste URL YouTube langsung dari browser[/dim]")


def flow_search() -> None:
    from melody.core.downloader import download_one
    from melody.core.searcher import search_youtube
    from melody.utils.ffmpeg import require_ffmpeg

    query = questionary.text("Cari lagu:", style=THEME).ask()
    if not query:
        return

    with console.status("[cyan]Mencari di YouTube...[/cyan]"):
        results = search_youtube(query.strip(), max_results=10)

    if not results:
        console.print("  [yellow]Tidak ada hasil ditemukan[/yellow]")
        return

    has_drm_hint = any(r.likely_drm for r in results)

    # Tampilkan tabel hasil sebelum checkbox
    t = Table(show_header=True, header_style="bold cyan", border_style="dim", box=None)
    t.add_column("#", width=3, justify="right", style="dim")
    t.add_column("Judul")
    t.add_column("Channel", style="dim")
    t.add_column("Durasi", justify="right", style="dim", width=7)
    for r in results:
        drm_tag = " [yellow][DRM?][/yellow]" if r.likely_drm else ""
        t.add_row(str(r.index), f"{r.title[:50]}{drm_tag}", r.channel[:25], r.duration_str)
    console.print()
    console.print(t)
    if has_drm_hint:
        console.print("  [dim yellow][DRM?] = kemungkinan terenkripsi, melody otomatis cari alternatif[/dim yellow]")
    console.print()

    # Checkbox pilih yang mau didownload
    choices = [
        questionary.Choice(
            f"{r.index:2}. {r.title[:48]}  ({r.duration_str})"
            + ("  [DRM?]" if r.likely_drm else ""),
            value=r,
        )
        for r in results
    ]

    selected = questionary.checkbox(
        "Pilih lagu yang mau didownload  (spasi = centang, enter = konfirmasi):",
        choices=choices,
        style=THEME,
    ).ask()

    if not selected:
        return

    require_ffmpeg()

    cfg = config_service.get_all()
    quality = _ask_quality(cfg.get("quality", "192"))
    if quality is None:
        return

    out_dir = _ask_output_dir(Path(cfg.get("output_dir", "~/Music")).expanduser())
    if out_dir is None:
        return

    skip = cfg.get("skip_history", True)

    # Buat index hasil search untuk fallback DRM
    all_results_by_idx = {r.index: r for r in results}
    console.print()

    for item in selected:
        console.print(f"  [cyan]↓[/cyan] {item.title}")
        r = download_one(item.url, out_dir, quality, skip_history=skip)

        if r.skipped:
            _result_skip()
        elif r.success:
            _result_ok(r.title, out_dir)
        elif r.drm:
            # Auto-coba video berikutnya dari hasil search yang tidak dipilih
            console.print(f"  [yellow]⊘ DRM protected — otomatis coba alternatif...[/yellow]")
            _try_drm_fallback(item, all_results_by_idx, selected, out_dir, quality, skip)
        else:
            _result_fail(r.error)


def flow_convert() -> None:
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

    from melody.core.converter import SUPPORTED_EXTS, convert_file, find_audio_files
    from melody.utils.ffmpeg import require_ffmpeg

    require_ffmpeg()

    raw = questionary.text(
        "File atau folder yang ingin dikonversi:",
        style=THEME,
    ).ask()

    if not raw:
        return

    p = Path(raw.strip()).expanduser()
    files: list[Path] = []

    if p.is_dir():
        files = find_audio_files(p)
        if not files:
            console.print(
                f"  [yellow]Tidak ada file audio di {p}[/yellow]\n"
                f"  [dim]Format didukung: {', '.join(SUPPORTED_EXTS)}[/dim]"
            )
            return
        console.print(f"  [cyan]{len(files)} file ditemukan[/cyan]")
    elif p.is_file():
        if p.suffix.lower() not in SUPPORTED_EXTS:
            console.print(f"  [red]Format tidak didukung:[/red] {p.suffix}")
            return
        files = [p]
    else:
        console.print(f"  [red]Tidak ditemukan:[/red] {p}")
        return

    cfg = config_service.get_all()
    quality = _ask_quality(cfg.get("quality", "192"))
    if quality is None:
        return

    same_folder = questionary.confirm(
        "Simpan MP3 di folder yang sama?",
        default=True,
        style=THEME,
    ).ask()

    if same_folder is None:
        return

    out_dir = files[0].parent if same_folder else _ask_output_dir(files[0].parent)
    if out_dir is None:
        return

    sample_rate = cfg.get("sample_rate", "44100")
    ok = failed = 0

    console.print()
    with Progress(
        SpinnerColumn(),
        TextColumn("  {task.description}"),
        BarColumn(bar_width=25),
        TextColumn("[dim]{task.completed}/{task.total}[/dim]"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Mengkonversi...", total=len(files))
        for f in files:
            progress.update(task, description=f"[cyan]{f.name[:45]}[/cyan]")
            out_path = out_dir / (f.stem + ".mp3")
            r = convert_file(f, out_path, quality, sample_rate, overwrite=True)
            if r.success:
                ok += 1
            else:
                failed += 1
                console.print(f"  [red]✗[/red] {f.name}: {r.error[:60]}")
            progress.advance(task)

    console.print(
        f"  [green]✓ Berhasil: {ok}[/green]"
        + (f"  [red]✗ Gagal: {failed}[/red]" if failed else "")
        + f"  [dim]→ {out_dir}[/dim]"
    )


def flow_history() -> None:
    from melody.services import history_service

    rows = history_service.get_recent(20)

    console.print()
    if not rows:
        console.print("  [dim]Belum ada history download[/dim]")
    else:
        t = Table(
            show_header=True,
            header_style="bold cyan",
            border_style="dim",
            box=None,
        )
        t.add_column("#", width=4, justify="right", style="dim")
        t.add_column("Judul")
        t.add_column("Kualitas", width=9, justify="center", style="dim")
        t.add_column("Tanggal", width=19, style="dim")
        for i, row in enumerate(rows, 1):
            date = row["downloaded_at"][:19].replace("T", " ") if row.get("downloaded_at") else "-"
            t.add_row(str(i), row["title"][:55], f"{row['quality']} kbps", date)
        console.print(t)
        console.print(f"\n  [dim]Database: {history_service.db_path()}[/dim]")

    console.print()
    action = questionary.select(
        "Aksi:",
        choices=[
            questionary.Choice("  Kembali ke menu", value="back"),
            questionary.Choice("  Hapus semua history", value="clear"),
        ],
        style=THEME,
    ).ask()

    if action == "clear":
        if questionary.confirm("Yakin hapus semua history?", default=False, style=THEME).ask():
            n = history_service.clear()
            console.print(f"  [yellow]{n} entri dihapus[/yellow]")


def flow_settings() -> None:
    cfg = config_service.get_all()

    action = questionary.select(
        "Ubah pengaturan:",
        choices=[
            questionary.Choice(
                f"  Kualitas default     [ {cfg['quality']} kbps ]",
                value="quality",
            ),
            questionary.Choice(
                f"  Folder download      [ {cfg['output_dir']} ]",
                value="output_dir",
            ),
            questionary.Choice(
                f"  Skip duplikat        [ {'Ya' if cfg['skip_history'] else 'Tidak'} ]",
                value="skip_history",
            ),
            questionary.Separator(),
            questionary.Choice("  Kembali ke menu", value=None),
        ],
        style=THEME,
    ).ask()

    if action == "quality":
        new_q = _ask_quality(cfg.get("quality", "192"))
        if new_q:
            config_service.set_value("quality", new_q)
            console.print(f"  [green]✓[/green] Kualitas diubah ke [bold]{new_q} kbps[/bold]")

    elif action == "output_dir":
        raw = questionary.text(
            f"Folder download baru  (sekarang: {cfg['output_dir']}):",
            style=THEME,
        ).ask()
        if raw:
            config_service.set_value("output_dir", raw.strip())
            console.print(f"  [green]✓[/green] Folder diubah ke [bold]{raw.strip()}[/bold]")

    elif action == "skip_history":
        new_val = questionary.confirm(
            "Skip otomatis jika lagu sudah pernah didownload?",
            default=cfg["skip_history"],
            style=THEME,
        ).ask()
        if new_val is not None:
            config_service.set_value("skip_history", str(new_val).lower())
            status = "aktif" if new_val else "nonaktif"
            console.print(f"  [green]✓[/green] Skip duplikat [bold]{status}[/bold]")


# ── Entry point ─────────────────────────────────────────────────

MENU_CHOICES = [
    questionary.Choice("  Download lagu / playlist dari YouTube", value="download"),
    questionary.Choice("  Download dari file daftar URL  (.txt)", value="batch"),
    questionary.Choice("  Cari lagu di YouTube",                  value="search"),
    questionary.Choice("  Konversi file audio lokal ke MP3",       value="convert"),
    questionary.Separator(),
    questionary.Choice("  Riwayat download",                       value="history"),
    questionary.Choice("  Pengaturan",                             value="settings"),
    questionary.Separator(),
    questionary.Choice("  Keluar",                                 value="exit"),
]

FLOWS = {
    "download": flow_download,
    "batch":    flow_batch,
    "search":   flow_search,
    "convert":  flow_convert,
    "history":  flow_history,
    "settings": flow_settings,
}


def run_interactive() -> None:
    banner()

    while True:
        try:
            choice = questionary.select(
                "Apa yang ingin kamu lakukan?",
                choices=MENU_CHOICES,
                style=THEME,
                use_shortcuts=False,
            ).ask()
        except KeyboardInterrupt:
            console.print("\n[dim]Sampai jumpa![/dim]")
            sys.exit(0)

        if choice is None or choice == "exit":
            console.print("[dim]Sampai jumpa![/dim]\n")
            sys.exit(0)

        console.print()
        try:
            FLOWS[choice]()
        except KeyboardInterrupt:
            console.print("\n  [dim]Dibatalkan — kembali ke menu[/dim]")
        except Exception as exc:
            console.print(f"\n  [red]Error:[/red] {exc}")

        console.print()
        console.rule(style="dim")
