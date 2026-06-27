"""Settings validation tests."""

import pytest
from pydantic import ValidationError

from app.config.settings import Settings


def test_default_model_is_gpt_oss_120b() -> None:
    settings = Settings()
    assert settings.model_name == "openai/gpt-oss-120b"


def test_log_level_is_normalized() -> None:
    settings = Settings(LOG_LEVEL="debug")
    assert settings.log_level == "DEBUG"


def test_invalid_log_level_fails() -> None:
    with pytest.raises(ValidationError):
        Settings(LOG_LEVEL="verbose")
