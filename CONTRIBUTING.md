# Contributing to melody

Terima kasih sudah tertarik berkontribusi! Panduan singkat ini membantu kamu mulai.

## Setup Dev

```bash
git clone https://github.com/0xAre/melody-cli
cd melody-cli
pip install -e ".[dev]"
```

Verifikasi:

```bash
melody --version
```

## Struktur Proyek

```
src/melody/
├── cli/
│   ├── app.py          # root Typer app + register subcommands
│   ├── interactive.py  # interactive wizard mode
│   └── commands/       # subcommand per file
├── core/
│   ├── downloader.py   # logika yt-dlp
│   ├── converter.py    # konversi file lokal
│   └── searcher.py     # YouTube search
├── services/
│   ├── config_service.py
│   └── history_service.py
└── utils/
    ├── ffmpeg.py
    └── validators.py
```

## Menambah Fitur

1. Fork repo → buat branch baru: `git checkout -b feat/nama-fitur`
2. Implementasi — ikuti pola yang sudah ada
3. Jalankan lint dan test:
   ```bash
   ruff check src/
   pytest tests/ -v
   ```
4. Buat PR ke branch `master`

## Melaporkan Bug

Cara tercepat: jalankan `melody report` dari terminal — browser langsung terbuka ke form GitHub Issues dengan info sistem sudah terisi otomatis.

Atau buka manual: [github.com/0xAre/melody-cli/issues/new](https://github.com/0xAre/melody-cli/issues/new?template=bug_report.md)

Sertakan:
- Versi melody (`melody --version`)
- OS dan versi Python
- Pesan error lengkap
- Langkah untuk mereproduksi

## Code Style

- Formatter/linter: **ruff** (`ruff check src/ --fix`)
- Max line length: 100
- Target: Python 3.10+
- Tidak perlu type annotation di semua tempat, tapi dianjurkan untuk fungsi publik

## PR Guidelines

- Satu PR, satu tujuan
- Judul PR: `feat:`, `fix:`, `docs:`, `refactor:` — ikuti conventional commits
- Tambahkan test jika menambah logika baru di `core/` atau `services/`
