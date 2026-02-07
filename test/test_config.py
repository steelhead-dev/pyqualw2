from pathlib import Path

import numpy as np
import pytest

from pyqualw2.config import Config
from pyqualw2.config.inputs import BathymetryInput, ProfileInput


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


@pytest.mark.skip
def test_from_csv(sample_w2_con, sample_bathymetry, sample_temperature):
    """Test that a config can be generated from data files."""
    Config.from_csv(sample_w2_con, sample_bathymetry, sample_temperature)


def test_load_bathymetry(sample_bathymetry):
    """Test that Bathymetry.from_file can load data from a file."""
    bathy = BathymetryInput.from_file(sample_bathymetry)
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


def test_load_temperature(sample_temperature):
    """Test that Temperature.from_file can load data from a file."""
    prof = ProfileInput.from_file(sample_temperature)

    assert prof.filename == sample_temperature
    assert prof.comment == (
        "File created from SJRRP Milerton Temperature Profile Viewer real string "
        "measurements"
    )
    assert prof.profile_file == "2025-05-15_profile.csv"

    # The profile file for this dataset has 216 entries in each layer-dependent dataset,
    # despite the fact that the bathymetry only defines 212 layers. The extra layers get
    # ignored by qualw2, evidently...
    assert prof.data["TemperC"].shape == (216,)
    assert prof.data["TDS mgl"].shape == (216,)
    assert prof.data["DO mgl"].shape == (216,)

    np.testing.assert_equal(prof.data["TemperC"][1:4], [20.35, 20.04, 19.93])
    np.testing.assert_equal(prof.data["TDS mgl"][6:9], [30.8, 29.5, 28.19])
    np.testing.assert_equal(prof.data["DO mgl"][1:4], [9.87, 9.94, 9.98])
