# 🎵 Melody CLI

> Fast, elegant YouTube → MP3 downloader for the terminal.
> Jalankan `melody` — navigasi dengan arrow keys, tidak perlu hafal command apapun.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

```
$ melody
```

```
╭────────────────────────────────────────────╮
│  melody  v1.0.0                            │
│  YouTube → MP3  •  Cari, Download, Konversi│
╰────────────────────────────────────────────╯

? Apa yang ingin kamu lakukan?
❯   Download lagu / playlist dari YouTube
    Download dari file daftar URL  (.txt)
    Cari lagu di YouTube
    Konversi file audio lokal ke MP3
  ──────────────
    Riwayat download
    Pengaturan
    Keluar
```

---

## Install

### Requirements

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) (wajib ada di PATH)

```bash
# Windows (winget)
winget install -e --id Gyan.FFmpeg

# Windows (Chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### Install Melody CLI

```bash
git clone https://github.com/0xAre/melody-cli
cd melody-cli
pip install -e .
```

---

## Usage

### Mode interaktif (direkomendasikan)

```bash
melody
```

Navigasi dengan arrow keys ↑↓, pilih dengan Enter. Tidak perlu hafal command apapun.

### Mode CLI (untuk scripting)

```bash
# Download satu lagu
melody download url "https://youtu.be/..."

# Download dengan kualitas dan folder kustom
melody download url "https://youtu.be/..." -o ~/Music -q 320

# Download playlist
melody download url "https://youtube.com/playlist?list=..."

# Download dari file daftar URL
melody download batch urls.txt -o ~/Music

# Cari YouTube
melody search query "bohemian rhapsody" --download

# Konversi file lokal
melody convert file ./dump -o ./musik -q 256

# Riwayat download
melody history show
melody history show --clear

# Konfigurasi
melody config show --show
melody config show --set quality=320
melody config show --set output_dir=D:/Musik
```

---

## Konfigurasi

Config tersimpan otomatis di `%APPDATA%\melody\config.toml`.

| Key | Default | Keterangan |
|---|---|---|
| `output_dir` | `~/Music` | Folder default download |
| `quality` | `192` | Bitrate MP3: 128/192/256/320 kbps |
| `skip_history` | `true` | Skip otomatis jika sudah pernah didownload |
| `sample_rate` | `44100` | Hz — standar kompatibel music box |

---

## Kompatibilitas Music Box

Melody menghasilkan MP3 yang kompatibel dengan hampir semua portable music player:
- Sample rate **44100 Hz**
- Codec **libmp3lame**
- **Stereo** (2 channel)
- ID3 metadata tertanam

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

[MIT](LICENSE) © 2025 aryansyach
