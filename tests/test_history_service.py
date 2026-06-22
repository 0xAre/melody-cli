import pytest
from pathlib import Path
from unittest.mock import patch


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Redirect DB ke folder temp agar test tidak kotor history asli."""
    db = tmp_path / "test_history.db"
    import melody.services.history_service as hs
    monkeypatch.setattr(hs, "_DB_PATH", db)
    yield db


def test_record_and_is_downloaded():
    from melody.services.history_service import record, is_downloaded, DownloadRecord

    assert not is_downloaded("abc123")

    record(DownloadRecord(
        video_id="abc123", title="Test Song",
        url="https://youtu.be/abc123", output_path="/tmp/test.mp3", quality="192"
    ))

    assert is_downloaded("abc123")


def test_get_recent():
    from melody.services.history_service import record, get_recent, DownloadRecord

    record(DownloadRecord("id1", "Song A", "url1", "/path/a.mp3", "128"))
    record(DownloadRecord("id2", "Song B", "url2", "/path/b.mp3", "320"))

    rows = get_recent(10)
    assert len(rows) == 2
    assert rows[0]["title"] == "Song B"  # paling baru duluan


def test_clear():
    from melody.services.history_service import record, clear, get_recent, DownloadRecord

    record(DownloadRecord("x1", "X", "u", "/x.mp3", "192"))
    assert clear() == 1
    assert get_recent() == []
