import numpy as np

from pyqualw2.config.inputs import BathymetryInput, ProfileInput, W2ConSimpleInput


def test_read_w2con_from_file(sample_w2_con):
    """Test that a W2ConSimpleInput can be generated from a w2_con.csv file."""
    w2con = W2ConSimpleInput.from_file(sample_w2_con)

    assert w2con.filename == sample_w2_con
    assert w2con.time_lineno == 27


def test_modify_w2con_times(sample_w2_con):
    """Check that modifying the w2_con.csv times works as intended."""
    w2con = W2ConSimpleInput.from_file(sample_w2_con)

    lines = w2con.content.splitlines()
    assert w2con.timedata == (35564.0416666667, 35569.9583333333, 1921)
    w2con.timedata = (0, 40, 1922)
    assert w2con.timedata == (0, 40, 1922)
    assert w2con.filename == sample_w2_con

    # No other lines should be touched
    new_lines = w2con.content.splitlines()
    assert new_lines[: w2con.time_lineno] == lines[: w2con.time_lineno]
    assert new_lines[w2con.time_lineno + 1 :] == lines[w2con.time_lineno + 1 :]


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


def test_load_temperature(sample_profile):
    """Test that Temperature.from_file can load data from a file."""
    prof = ProfileInput.from_file(sample_profile)

    assert prof.filename == sample_profile
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

    np.testing.assert_equal(prof.data["TemperC"].to_numpy()[1:4], [20.35, 20.04, 19.93])
    np.testing.assert_equal(prof.data["TDS mgl"].to_numpy()[6:9], [30.8, 29.5, 28.19])
    np.testing.assert_equal(prof.data["DO mgl"].to_numpy()[1:4], [9.87, 9.94, 9.98])


def test_write_bathymetry(sample_bathymetry, tmp_path):
    """Test that writing bathymetry data to a file works as intended."""
    path = tmp_path / "test.csv"
    bathy = BathymetryInput.from_file(sample_bathymetry)
    bathy.to_file(path)


def test_write_profile(sample_profile, tmp_path):
    """Test that writing profile data to a file works as intended."""
    path = tmp_path / "test.npt"
    prof = ProfileInput.from_file(sample_profile)

    with open(sample_profile) as f:
        lines = f.readlines()

    prof.to_file(path)
    with open(path) as f:
        newlines = f.readlines()

    # Check that the new file is the same number of lines as the old
    assert len(newlines) == len(lines)
    assert newlines[0].startswith("Profile file:")


def test_write_w2con(sample_w2_con, tmp_path):
    """Test that writing the w2_con file to disk works as intended."""
    path = tmp_path / "test.csv"
    obj = W2ConSimpleInput.from_file(sample_w2_con)

    with open(sample_w2_con) as f:
        lines = f.readlines()

    assert obj.timedata != (1, 2, 3)
    obj.timedata = (1, 2, 3)
    obj.to_file(path)
    with open(path) as f:
        newlines = f.readlines()

    assert len(newlines) == len(lines)
    assert newlines[: obj.time_lineno] == lines[: obj.time_lineno]
    assert newlines[obj.time_lineno + 1 :] == lines[obj.time_lineno + 1 :]
    assert newlines[obj.time_lineno].startswith("1,2,3,")
