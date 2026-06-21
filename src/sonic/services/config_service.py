"""
Config permanen disimpan di:
  Windows : %APPDATA%/sonic/config.toml
  Linux   : ~/.config/sonic/config.toml
  macOS   : ~/Library/Application Support/sonic/config.toml
"""
import tomllib
from pathlib import Path

import tomli_w
from platformdirs import user_config_dir

DEFAULTS: dict = {
    "output_dir": str(Path.home() / "Music"),
    "quality": "192",
    "skip_history": True,
    "sample_rate": "44100",
}

_CONFIG_PATH = Path(user_config_dir("sonic")) / "config.toml"


def _load_raw() -> dict:
    if _CONFIG_PATH.exists():
        with open(_CONFIG_PATH, "rb") as f:
            return tomllib.load(f)
    return {}


def _save_raw(data: dict) -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_CONFIG_PATH, "wb") as f:
        tomli_w.dump(data, f)


def get_all() -> dict:
    """Kembalikan config lengkap (defaults di-merge dengan file user)."""
    merged = dict(DEFAULTS)
    merged.update(_load_raw())
    return merged


def get(key: str):
    """Baca satu nilai config."""
    return get_all().get(key)


def set_value(key: str, value: str) -> None:
    """Tulis satu nilai config ke file."""
    if key not in DEFAULTS:
        raise KeyError(f"Config key tidak dikenal: '{key}'. Tersedia: {list(DEFAULTS)}")
    data = _load_raw()
    # Konversi tipe sesuai default
    default_val = DEFAULTS[key]
    if isinstance(default_val, bool):
        data[key] = value.lower() in ("true", "1", "yes")
    else:
        data[key] = value
    _save_raw(data)


def reset() -> None:
    """Hapus file config (kembali ke defaults)."""
    if _CONFIG_PATH.exists():
        _CONFIG_PATH.unlink()


def config_path() -> Path:
    return _CONFIG_PATH
