from pathlib import Path

import numpy as np
import pytest

from pyqualw2.config import Config
from pyqualw2.data import Bathymetry, Temperature


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


@pytest.mark.skip
def test_from_csv(sample_w2_con, sample_bathymetry, sample_temperature):
    """Test that a config can be generated from data files."""
    Config.from_csv(sample_w2_con, sample_bathymetry, sample_temperature)


def test_load_bathymetry(sample_bathymetry):
    """Test that a Bathymetry can be loaded from a file on disk."""
    bathy = Bathymetry.from_file(sample_bathymetry)
    assert bathy.filename == sample_bathymetry
    np.testing.assert_equal(
        bathy.segment_data["DLX [m]"][0:3].to_numpy(), [0, 824.71, 824.71]
    )
    np.testing.assert_equal(
        bathy.segment_data["ELWS [m]"][0:3].to_numpy(), [171.73, 171.73, 171.73]
    )
    np.testing.assert_equal(
        bathy.segment_data["PHI0 [rad]"][0:3].to_numpy(), [0.37, 0.37, -0.25]
    )
    np.testing.assert_equal(bathy.segment_data["FRIC"][0:3].to_numpy(), [70, 70, 70])

    # 48 segments and 212 layers
    assert bathy.data.shape == (212, 48)
