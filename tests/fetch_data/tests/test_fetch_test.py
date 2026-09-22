import pytest
from fetch_data.main import fetch_test


url = secrets.URL


def test_len():
    response = fetch_test(url)
    length = len(response)
    assert length == 7
