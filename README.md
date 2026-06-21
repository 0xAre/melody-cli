# 🎵 sonic

> Fast, elegant YouTube → MP3 downloader for the terminal.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

```
sonic download url "https://youtu.be/..." -q 320
sonic search "bohemian rhapsody" --download
sonic batch playlist.txt -o ~/Music
```

---

## Install

### Requirements

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) (wajib ada di PATH)

```bash
# Windows (Chocolatey)
choco install ffmpeg

# Windows (winget)
winget install -e --id Gyan.FFmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### Install sonic

```bash
# Clone repo
git clone https://github.com/aryansyach/sonic-dl
cd sonic-dl

# Install (development)
pip install -e .

# Atau install langsung
pip install sonic-dl
```

---

## Usage

### Download satu lagu

```bash
sonic download url "https://youtu.be/dQw4w9WgXcQ"

# Pilih folder dan kualitas
sonic download url "https://youtu.be/dQw4w9WgXcQ" -o ~/Music -q 320
```

### Download playlist

```bash
sonic download url "https://www.youtube.com/playlist?list=PLxxxxx"
```

### Download dari file (batch)

```bash
# Buat file urls.txt
# https://youtu.be/abc
# https://youtu.be/def

sonic download batch urls.txt -o ~/Music
```

### Cari dan download

```bash
# Tampilkan hasil saja
sonic search query "bohemian rhapsody"

# Tampilkan + pilih untuk download
sonic search query "bohemian rhapsody" --download
```

### Konversi file lokal

```bash
# Satu file
sonic convert file lagu.webm -o ./output

# Satu folder
sonic convert file ./dump -o ./musik -q 256 --overwrite
```

### Konfigurasi

```bash
# Lihat config aktif
sonic config show --show

# Ubah satu setting
sonic config show --set output_dir=D:/Musik
sonic config show --set quality=320

# Reset ke default
sonic config show --reset
```

### Riwayat download

```bash
sonic history show
sonic history show --last 50
sonic history show --find "Coldplay"
sonic history show --clear
```

---

## Config

Config disimpan di `%APPDATA%\sonic\config.toml` (Windows) / `~/.config/sonic/config.toml`.

| Key | Default | Keterangan |
|---|---|---|
| `output_dir` | `~/Music` | Folder default download |
| `quality` | `192` | Bitrate MP3: 128/192/256/320 kbps |
| `skip_history` | `true` | Skip otomatis jika sudah pernah didownload |
| `sample_rate` | `44100` | Hz — standar kompatibel music box |

---

## Kompatibilitas Music Box

sonic menghasilkan MP3 yang kompatibel dengan hampir semua portable music player:
- Sample rate **44100 Hz**
- Codec **libmp3lame**
- **Stereo** (2 channel)
- ID3 metadata tertanam

---

## Development

```bash
git clone https://github.com/aryansyach/sonic-dl
cd sonic-dl
pip install -e ".[dev]"

# Jalankan tests
pytest tests/ -v
```

---

## License

[MIT](LICENSE) © 2025 aryansyach
