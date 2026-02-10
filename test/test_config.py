import pytest

from pyqualw2.config import Config


@pytest.mark.skip
def test_from_csv(sample_w2_con, sample_bathymetry, sample_temperature):
    """Test that a config can be generated from data files."""
    Config.from_csv(sample_w2_con, sample_bathymetry, sample_temperature)
