# 🎵 Melody CLI

> Fast, elegant YouTube → MP3 downloader for the terminal.
> Navigasi dengan arrow keys — tidak perlu hafal command apapun.

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
    Konversi file audio lokal ke MP3
  ──────────────
    Riwayat download
    Pengaturan
    Keluar
```

---

## Install

### Windows (satu command)

Buka **PowerShell**, paste ini, tekan Enter:

```powershell
irm https://raw.githubusercontent.com/0xAre/melody-cli/master/install.ps1 | iex
```

Script akan otomatis:
- cek Python & FFmpeg
- install `pipx` jika belum ada
- install `melody` dan daftarkan ke PATH

### Linux / macOS

```bash
curl -sSL https://raw.githubusercontent.com/0xAre/melody-cli/master/install.sh | bash
```

### Manual (semua OS)

```bash
pip install git+https://github.com/0xAre/melody-cli.git
```

---

## Persyaratan

| | |
|---|---|
| **Python** | 3.10 atau lebih baru |
| **FFmpeg** | wajib ada di PATH untuk konversi MP3 |

**Install FFmpeg:**

```bash
# Windows
winget install -e --id Gyan.FFmpeg

# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg
```

---

## Penggunaan

### Mode interaktif (direkomendasikan)

```bash
melody
```

Jalankan saja `melody`, navigasi dengan ↑↓ arrow keys. Tidak perlu hafal flag apapun.

**Alur queue** — kumpulkan dulu, download sekaligus:
```
Cari → pilih → Tambah ke antrian
Cari → pilih → Tambah ke antrian
...
Download antrian  (proses semua sekaligus)
```

### Mode CLI (untuk scripting)

```bash
# Download lagu / playlist
melody get "https://youtu.be/..."
melody get "https://youtube.com/playlist?list=..." -o ~/Music -q 320

# Cari dan download
melody search query "bohemian rhapsody"

# Konversi file lokal
melody convert file ./dump -o ./musik

# Riwayat
melody history show

# Konfigurasi
melody config show
melody config show --set quality=320
melody config show --set output_dir=D:/Musik
```

---

## Konfigurasi

Tersimpan otomatis di `%APPDATA%\melody\config.toml` (Windows) atau `~/.config/melody/config.toml`.

| Key | Default | Keterangan |
|---|---|---|
| `output_dir` | `~/Music` | Folder default download |
| `quality` | `192` | Bitrate MP3: 128 / 192 / 256 / 320 kbps |
| `skip_history` | `true` | Skip otomatis jika sudah pernah didownload |
| `sample_rate` | `44100` | Hz — kompatibel dengan portable music player |

---

## Kompatibilitas Music Player

Melody menghasilkan MP3 yang kompatibel dengan hampir semua portable music player (music box, Acome, dll):

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

[MIT](LICENSE) © 2025 [0xAre](https://github.com/0xAre)
