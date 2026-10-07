"""Shared fixtures: a synthetic market so pipeline tests need no network or data files."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def market() -> pd.DataFrame:
    """Five years of random-walk prices and random GPR on business days."""
    rng = np.random.default_rng(0)
    days = pd.bdate_range("2012-01-02", "2016-12-30", name="date")

    def walk() -> np.ndarray:
        return 100 * np.exp(np.cumsum(rng.normal(0, 0.01, len(days))))

    return pd.DataFrame(
        {
            "ita": walk(),
            "brent": walk(),
            "gprd_act": rng.gamma(2, 50, len(days)),
            "gprd_threat": rng.gamma(2, 50, len(days)),
        },
        index=days,
    )
