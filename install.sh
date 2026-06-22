#!/usr/bin/env bash
# Melody CLI — Linux/macOS Installer
# Usage: curl -sSL https://raw.githubusercontent.com/0xAre/melody-cli/master/install.sh | bash

set -e

GREEN='\033[0;32m' CYAN='\033[0;36m' YELLOW='\033[1;33m' RED='\033[0;31m' NC='\033[0m'

echo ""
echo -e "  ${CYAN}melody-cli installer${NC}"
echo "  ─────────────────────────────────────"
echo ""

# ── 1. Cek Python ────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo -e "  ${RED}[!] Python 3 tidak ditemukan.${NC}"
    echo "      macOS: brew install python"
    echo "      Ubuntu: sudo apt install python3 python3-pip"
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo -e "  ${RED}[!] Python 3.10+ dibutuhkan (kamu punya $PY_VER)${NC}"
    exit 1
fi
echo -e "  ${GREEN}[ok] Python $PY_VER${NC}"

# ── 2. Cek FFmpeg ─────────────────────────────────────────────────
if command -v ffmpeg &>/dev/null; then
    echo -e "  ${GREEN}[ok] FFmpeg sudah ada${NC}"
else
    echo -e "  ${YELLOW}[!] FFmpeg belum ada.${NC}"
    echo "      macOS:  brew install ffmpeg"
    echo "      Ubuntu: sudo apt install ffmpeg"
    echo ""
fi

# ── 3. Install pipx jika belum ada ───────────────────────────────
if ! command -v pipx &>/dev/null; then
    echo -e "  ${CYAN}Installing pipx...${NC}"
    python3 -m pip install --user pipx --quiet
    python3 -m pipx ensurepath
fi
echo -e "  ${GREEN}[ok] pipx${NC}"

# ── 4. Install melody ─────────────────────────────────────────────
echo -e "  ${CYAN}Installing melody-cli...${NC}"
pipx install git+https://github.com/0xAre/melody-cli.git --force

echo ""
echo "  ─────────────────────────────────────"
echo -e "  ${GREEN}Selesai! Jalankan: melody${NC}"
echo ""
echo "  Jika 'melody' tidak ditemukan, jalankan:"
echo "  python3 -m pipx ensurepath"
echo "  lalu restart terminal."
echo ""
