from pathlib import Path

import pytest

from pyqualw2.config import Config


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
    return sample_data / "w2_con.csv"


def test_from_csv(sample_w2_con, sample_bathymetry, sample_temperature):
    """Test that a config can be generated from data files."""
    Config.from_csv(sample_w2_con, sample_bathymetry, sample_temperature)
