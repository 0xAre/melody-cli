# Melody CLI — Windows Installer
# Usage: irm https://raw.githubusercontent.com/0xAre/melody-cli/master/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  melody-cli installer" -ForegroundColor Cyan
Write-Host "  ─────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

# ── 1. Cek Python ────────────────────────────────────────────────
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "  [!] Python tidak ditemukan." -ForegroundColor Red
    Write-Host "      Install dari: https://python.org/downloads" -ForegroundColor Yellow
    Write-Host "      Centang 'Add Python to PATH' saat install." -ForegroundColor Yellow
    exit 1
}

$pyVer = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$pyMinor = [int](python -c "import sys; print(sys.version_info.minor)")
$pyMajor = [int](python -c "import sys; print(sys.version_info.major)")

if ($pyMajor -lt 3 -or ($pyMajor -eq 3 -and $pyMinor -lt 10)) {
    Write-Host "  [!] Python 3.10+ dibutuhkan (kamu punya $pyVer)" -ForegroundColor Red
    exit 1
}
Write-Host "  [ok] Python $pyVer" -ForegroundColor Green

# ── 2. Cek FFmpeg ─────────────────────────────────────────────────
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Host "  [ok] FFmpeg sudah ada" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  [!] FFmpeg belum ada — dibutuhkan untuk konversi MP3." -ForegroundColor Yellow
    Write-Host "      Install dengan salah satu cara:" -ForegroundColor Yellow
    Write-Host "        winget install -e --id Gyan.FFmpeg" -ForegroundColor Cyan
    Write-Host "        choco install ffmpeg" -ForegroundColor Cyan
    Write-Host ""
    $cont = Read-Host "  Lanjut install melody tanpa FFmpeg dulu? (y/n)"
    if ($cont -ne "y") { exit 0 }
}

# ── 3. Install pipx jika belum ada ───────────────────────────────
if (-not (Get-Command pipx -ErrorAction SilentlyContinue)) {
    Write-Host "  Installing pipx..." -ForegroundColor Cyan
    pip install pipx --quiet
    python -m pipx ensurepath | Out-Null
    # Reload PATH sesi ini
    $userPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
    $machinePath = [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
    $env:PATH = "$userPath;$machinePath"
}
Write-Host "  [ok] pipx" -ForegroundColor Green

# ── 4. Install melody ─────────────────────────────────────────────
Write-Host "  Installing melody-cli..." -ForegroundColor Cyan
pipx install git+https://github.com/0xAre/melody-cli.git --force
# Catatan: package PyPI tersedia sebagai: pip install melody-mp3

Write-Host ""
Write-Host "  ─────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  Selesai! Jalankan: melody" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Jika command 'melody' tidak ditemukan," -ForegroundColor DarkGray
Write-Host "  restart terminal atau jalankan:" -ForegroundColor DarkGray
Write-Host "  python -m pipx ensurepath" -ForegroundColor DarkGray
Write-Host ""
