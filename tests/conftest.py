import pytest
from config.settings import Settings

@pytest.fixture
def test_settings():
    return Settings(DATABASE_URL="sqlite:///:memory:") 