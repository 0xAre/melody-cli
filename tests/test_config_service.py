import pytest
from pathlib import Path
from unittest.mock import patch


def test_get_all_returns_defaults():
    from sonic.services.config_service import get_all, DEFAULTS
    cfg = get_all()
    for key in DEFAULTS:
        assert key in cfg


def test_validate_quality_valid():
    from sonic.utils.validators import validate_quality
    assert validate_quality("192") == "192"
    assert validate_quality("320") == "320"


def test_validate_quality_invalid():
    from sonic.utils.validators import validate_quality
    with pytest.raises(ValueError):
        validate_quality("999")


def test_extract_video_id():
    from sonic.utils.validators import extract_video_id
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://example.com/page") is None
