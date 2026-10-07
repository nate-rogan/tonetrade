"""Unit tests for tonetrade.sources (read the committed GPR snapshot; no network)."""

import tonetrade as tt


def test_fetch_gpr_data() -> None:
    result = tt.sources.fetch_gpr_data()
    assert list(result.columns) == ["gprd_act", "gprd_threat"]
    assert result.index.name == "date"
