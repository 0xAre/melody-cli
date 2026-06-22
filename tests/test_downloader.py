from unittest.mock import patch, MagicMock
from pathlib import Path


def test_download_skips_known_video(tmp_path):
    from melody.core.downloader import download_one

    with patch("melody.core.downloader.history_service.is_downloaded", return_value=True):
        r = download_one("https://youtu.be/dQw4w9WgXcQ", tmp_path, "192", skip_history=True)

    assert r.skipped is True
    assert r.success is True


def test_download_records_history(tmp_path):
    from melody.core.downloader import download_one

    fake_info = {
        "id": "testid123",
        "title": "Test Video",
        "ext": "mp3",
        "webpage_url": "https://youtu.be/testid123",
    }

    mock_ydl = MagicMock()
    mock_ydl.__enter__ = lambda s: s
    mock_ydl.__exit__ = MagicMock(return_value=False)
    mock_ydl.extract_info.return_value = fake_info
    mock_ydl.prepare_filename.return_value = str(tmp_path / "Test Video.mp3")

    with patch("melody.core.downloader.history_service.is_downloaded", return_value=False), \
         patch("melody.core.downloader.history_service.record") as mock_record, \
         patch("melody.core.downloader.yt_dlp.YoutubeDL", return_value=mock_ydl), \
         patch("melody.core.downloader.progress_service.make_progress"):
        r = download_one("https://youtu.be/testid123", tmp_path, "192",
                         skip_history=True, show_progress=False)

    assert r.success is True
    assert r.title == "Test Video"
    mock_record.assert_called_once()
