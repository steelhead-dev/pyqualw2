from pathlib import Path

import pytest


@pytest.fixture
def sample_data() -> Path:
    """Get the path to the sample data."""
    return Path(__file__).parent / "sample_data"


@pytest.fixture
def sample_w2_con(sample_data) -> Path:
    """Get the path to the w2_con file."""
    return sample_data / "w2_con.csv"


@pytest.fixture
def sample_bathymetry(sample_data) -> Path:
    """Get the path to the bathymetry file."""
    return sample_data / "mbth_wb1.csv"


@pytest.fixture
def sample_temperature(sample_data) -> Path:
    """Get the path to the temperature file."""
    return sample_data / "mvpr1.npt"
