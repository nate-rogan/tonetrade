"""
Unit tests for the ToneTrade sources module.
This module contains unit tests for verifying the functionality of the data source
functions in the ToneTrade project.
"""

from tonetrade.sources import fetch_text_test


def test_fetch_text_test() -> None:
    result = fetch_text_test()
    assert isinstance(result, str)
    assert result == "Test text data"
