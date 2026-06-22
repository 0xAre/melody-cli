```
███╗   ███╗███████╗██╗      ██████╗ ██████╗ ██╗   ██╗
████╗ ████║██╔════╝██║     ██╔═══██╗██╔══██╗╚██╗ ██╔╝
██╔████╔██║█████╗  ██║     ██║   ██║██║  ██║ ╚████╔╝
██║╚██╔╝██║██╔══╝  ██║     ██║   ██║██║  ██║  ╚██╔╝
██║ ╚═╝ ██║███████╗███████╗╚██████╔╝██████╔╝   ██║
╚═╝     ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═════╝    ╚═╝

              ♪  YouTube → MP3 Downloader  ♪
```

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/melody-mp3?color=00d7af&label=PyPI&style=flat-square)](https://pypi.org/project/melody-mp3)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)](https://python.org)
[![CI](https://img.shields.io/github/actions/workflow/status/0xAre/melody-cli/ci.yml?label=CI&style=flat-square)](https://github.com/0xAre/melody-cli/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

**Download musik dari YouTube langsung ke MP3 — tanpa perlu hafal command apapun.**

</div>

---

## Install

```bash
pip install melody-mp3
```

Selesai. **FFmpeg sudah termasuk** — tidak perlu install manual, otomatis diunduh saat pertama kali dibutuhkan.

### One-liner installer

**Windows** (PowerShell):
```powershell
irm https://raw.githubusercontent.com/0xAre/melody-cli/master/install.ps1 | iex
```

**Linux / macOS**:
```bash
curl -sSL https://raw.githubusercontent.com/0xAre/melody-cli/master/install.sh | bash
```

> Butuh Python 3.10+. Cek dengan `python --version`.

---

## Cara pakai

Jalankan satu command:

```bash
melody
```

Navigasi dengan arrow keys, pilih dengan Enter. Tidak perlu hafal syntax apapun.

```
? Apa yang ingin kamu lakukan?
❯   Download lagu / playlist dari YouTube
    Download dari file daftar URL (.txt)
    Cari lagu di YouTube
  ──────── Antrian [3 lagu] ───────────
    Antrian [3 lagu]  —  lihat & kelola
    Download antrian  (3 lagu)
  ─────────────────────────────────────
    Konversi file audio lokal ke MP3
    Riwayat download
    Pengaturan
    Laporkan bug
    Keluar
```

### Queue — kumpulkan dulu, download sekaligus

```
melody
  → Cari lagu → pilih → Tambah ke antrian
  → Cari lagu → pilih → Tambah ke antrian
  → Download antrian   ← semua diproses sekaligus
```

### CLI langsung

```bash
# Download satu lagu
melody get "https://youtu.be/..."

# Download playlist
melody get "https://youtube.com/playlist?list=..." -o ~/Music -q 320

# Cari dan download
melody search query "bohemian rhapsody"

# Konversi file lokal ke MP3
melody convert file ./folder -o ./output

# Riwayat
melody history show

# Konfigurasi
melody config show
melody config set quality=320
melody config set output_dir=D:/Musik

# Laporkan bug (buka GitHub Issues otomatis)
melody report
```

---

## Fitur

| | |
|---|---|
| **Zero setup** | FFmpeg diunduh otomatis jika belum ada di sistem |
| **Interactive wizard** | Navigasi arrow keys, tidak perlu hafal command |
| **Queue system** | Kumpulkan dari beberapa pencarian, download sekaligus |
| **YouTube Music** | URL `music.youtube.com` otomatis dikonversi |
| **Auto-fallback DRM** | Video protected? melody coba versi alternatif |
| **History & dedup** | Tidak download ulang lagu yang sudah ada |
| **Playlist** | Download seluruh playlist sekaligus |
| **Config permanen** | Kualitas, folder output, sample rate tersimpan |
| **Bug reporter** | `melody report` langsung buka GitHub Issues dengan info sistem |

---

## Konfigurasi

Tersimpan otomatis di:
- Windows: `%APPDATA%\melody\config.toml`
- Linux/macOS: `~/.config/melody/config.toml`

| Key | Default | Keterangan |
|---|---|---|
| `output_dir` | `~/Music` | Folder tujuan download |
| `quality` | `192` | Bitrate MP3: `128` / `192` / `256` / `320` kbps |
| `skip_history` | `true` | Lewati otomatis jika sudah pernah didownload |
| `sample_rate` | `44100` | Hz — kompatibel dengan portable music player |

---

## Contributing

Lihat [CONTRIBUTING.md](CONTRIBUTING.md) untuk panduan setup dev dan cara membuat PR.

Bug? Jalankan `melody report` atau buka [issue di sini](https://github.com/0xAre/melody-cli/issues/new?template=bug_report.md).

---

## License

[MIT](LICENSE) © 2025 [0xAre](https://github.com/0xAre)
