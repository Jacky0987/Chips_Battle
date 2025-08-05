import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from services.currency_service import CurrencyService
from tests.conftest import test_settings

@pytest.fixture
def currency_service():
    return CurrencyService()

def test_load_currencies(currency_service):
    currencies = currency_service.currencies
    assert len(currencies) > 0

def test_update_rates(currency_service):
    # Simplified test
    old_rate = currency_service.currencies['USD'].current_rate
    currency_service.update_exchange_rates()
    new_rate = currency_service.currencies['USD'].current_rate
    assert new_rate != old_rate 