"""
History download disimpan di SQLite:
  Windows : %LOCALAPPDATA%/sonic/history.db
  Linux   : ~/.local/share/sonic/history.db
"""
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from platformdirs import user_data_dir

_DB_PATH = Path(user_data_dir("sonic")) / "history.db"

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS downloads (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id      TEXT    UNIQUE,
    title         TEXT,
    url           TEXT,
    output_path   TEXT,
    quality       TEXT,
    downloaded_at TEXT
);
"""


@dataclass
class DownloadRecord:
    video_id: str
    title: str
    url: str
    output_path: str
    quality: str
    downloaded_at: str = ""


def _connect() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.execute(_CREATE_SQL)
    conn.commit()
    return conn


def is_downloaded(video_id: str) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM downloads WHERE video_id = ?", (video_id,)
        ).fetchone()
    return row is not None


def record(rec: DownloadRecord) -> None:
    now = datetime.now(tz=timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO downloads
                (video_id, title, url, output_path, quality, downloaded_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (rec.video_id, rec.title, rec.url, rec.output_path, rec.quality, now),
        )
        conn.commit()


def get_recent(n: int = 20) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT video_id, title, url, quality, downloaded_at "
            "FROM downloads ORDER BY id DESC LIMIT ?",
            (n,),
        ).fetchall()
    return [
        {"video_id": r[0], "title": r[1], "url": r[2], "quality": r[3], "downloaded_at": r[4]}
        for r in rows
    ]


def clear() -> int:
    """Hapus semua history, kembalikan jumlah baris yang dihapus."""
    with _connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
        conn.execute("DELETE FROM downloads")
        conn.commit()
    return count


def db_path() -> Path:
    return _DB_PATH
