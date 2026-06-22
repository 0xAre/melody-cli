"""
Konversi file audio lokal ke MP3 menggunakan FFmpeg langsung.
"""
import subprocess
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_EXTS = (".webm", ".m4a", ".wav", ".flac", ".opus", ".ogg", ".aac", ".wma", ".mp4")


@dataclass
class ConvertResult:
    success: bool
    input_path: str = ""
    output_path: str = ""
    size_mb: float = 0.0
    error: str = ""


def convert_file(
    input_path: Path,
    output_path: Path,
    quality: str = "192",
    sample_rate: str = "44100",
    overwrite: bool = False,
) -> ConvertResult:
    if not input_path.exists():
        return ConvertResult(success=False, input_path=str(input_path), error="File tidak ditemukan")

    if output_path.exists() and not overwrite:
        return ConvertResult(
            success=False, input_path=str(input_path),
            output_path=str(output_path), error="File output sudah ada (gunakan --overwrite)"
        )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-codec:a", "libmp3lame",
        "-b:a", f"{quality}k",
        "-ar", sample_rate,
        "-ac", "2",
        "-loglevel", "error",
        str(output_path),
    ]

    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            return ConvertResult(
                success=False,
                input_path=str(input_path),
                output_path=str(output_path),
                error=r.stderr.strip()[:300],
            )
        size = output_path.stat().st_size / (1024 * 1024)
        return ConvertResult(
            success=True,
            input_path=str(input_path),
            output_path=str(output_path),
            size_mb=round(size, 2),
        )
    except FileNotFoundError:
        return ConvertResult(
            success=False, input_path=str(input_path), error="FFmpeg tidak ditemukan"
        )
    except Exception as e:
        return ConvertResult(success=False, input_path=str(input_path), error=str(e))


def find_audio_files(directory: Path) -> list[Path]:
    """Cari semua file audio yang didukung di direktori (tidak rekursif)."""
    files = [
        f for f in directory.iterdir()
        if f.is_file()
        and f.suffix.lower() in SUPPORTED_EXTS
        and not f.name.endswith(".part")
    ]
    return sorted(files)
