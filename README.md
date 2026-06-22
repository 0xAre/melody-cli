# 🎵 Melody CLI

> YouTube → MP3 downloader dengan interactive wizard di terminal.
> Navigasi dengan arrow keys — tidak perlu hafal command apapun.

[![PyPI](https://img.shields.io/pypi/v/melody-mp3?color=00d7af&label=PyPI)](https://pypi.org/project/melody-mp3)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

```
╭────────────────────────────────────────────╮
│  melody  v1.0.0                            │
│  YouTube → MP3  •  Cari, Download, Konversi│
╰────────────────────────────────────────────╯

? Apa yang ingin kamu lakukan?
❯   Download lagu / playlist dari YouTube
    Download dari file daftar URL  (.txt)
    Cari lagu di YouTube
  ──────── Antrian [3 lagu] ────────────
    Antrian [3 lagu]  —  lihat & kelola
    Download antrian  (3 lagu)
  ──────────────────────────────────────
    Konversi file audio lokal ke MP3
    Riwayat download
    Pengaturan
    Keluar
```

---

## Install

### Windows — satu command

Buka **PowerShell**, paste, tekan Enter:

```powershell
irm https://raw.githubusercontent.com/0xAre/melody-cli/master/install.ps1 | iex
```

Otomatis cek Python, install pipx, install melody, daftarkan ke PATH.

### Linux / macOS

```bash
curl -sSL https://raw.githubusercontent.com/0xAre/melody-cli/master/install.sh | bash
```

### Via pip / pipx

```bash
# pip
pip install melody-mp3

# pipx (direkomendasikan — environment terisolasi)
pipx install melody-mp3
```

---

## Persyaratan

| | |
|---|---|
| **Python** | 3.10+ |
| **FFmpeg** | wajib ada di PATH untuk konversi MP3 |

```bash
# Windows
winget install -e --id Gyan.FFmpeg

# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg
```

---

## Fitur

- **Interactive wizard** — navigasi arrow keys, tidak perlu hafal command apapun
- **Queue system** — kumpulkan lagu dari beberapa pencarian, download sekaligus
- **Cari YouTube** langsung dari terminal
- **Support YouTube Music URLs** (`music.youtube.com`) — otomatis dikonversi
- **Auto-fallback DRM** — jika video protected, otomatis coba versi lain
- **Download playlist** sekaligus
- **History & dedup** — tidak download ulang lagu yang sama
- **Config permanen** — kualitas, folder output, sample rate
- **Kompatibel music box** — 44100 Hz, libmp3lame, stereo

---

## Penggunaan

### Mode interaktif (direkomendasikan)

```bash
melody
```

Jalankan `melody`, navigasi ↑↓, pilih Enter. Tidak perlu hafal apapun.

**Alur queue — kumpulkan dulu, download sekaligus:**

```
melody
  → Cari lagu di YouTube  →  pilih  →  Tambah ke antrian
  → Cari lagu di YouTube  →  pilih  →  Tambah ke antrian
  → Download antrian  (proses semua sekaligus)
```

### Mode CLI

```bash
# Download satu lagu atau playlist
melody get "https://youtu.be/..."
melody get "https://youtube.com/playlist?list=..." -o ~/Music -q 320

# Cari YouTube
melody search query "bohemian rhapsody"

# Konversi file audio lokal
melody convert file ./folder -o ./output

# Riwayat download
melody history show

# Konfigurasi
melody config show
melody config show --set quality=320
melody config show --set output_dir=D:/Musik
```

---

## Konfigurasi

Tersimpan di `%APPDATA%\melody\config.toml` (Windows) / `~/.config/melody/config.toml` (Linux/macOS).

| Key | Default | Keterangan |
|---|---|---|
| `output_dir` | `~/Music` | Folder default download |
| `quality` | `192` | Bitrate MP3: 128 / 192 / 256 / 320 kbps |
| `skip_history` | `true` | Skip otomatis jika sudah pernah didownload |
| `sample_rate` | `44100` | Hz — kompatibel portable music player |

---

## Development

```bash
git clone https://github.com/0xAre/melody-cli
cd melody-cli
pip install -e ".[dev]"
pytest tests/ -v
```

---

## License

[MIT](LICENSE) © 2025 [0xAre](https://github.com/0xAre)
