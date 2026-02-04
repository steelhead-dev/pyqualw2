import re
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import StringIO
from os import PathLike
from pathlib import Path
from typing import Self

import pandas as pd


class BaseData(ABC):
    """Base class for all data types."""

    @classmethod
    @abstractmethod
    def from_file(cls, file: PathLike) -> Self:
        """Parse a data file to a python object.

        Parameters
        ----------
        file : PathLike
            Path to the data file

        Returns
        -------
        Self
            An object containing the data from the file
        """


@dataclass
class Bathymetry(BaseData):
    """Container for Bathymetry data."""

    data: pd.DataFrame
    segment_data: pd.DataFrame
    ignored: list[str]
    filename: PathLike | None = None
    comment: str | None = None

    @classmethod
    def from_file(cls, filename: PathLike) -> Self:
        """Parse a bathymetry file.

        Parameters
        ----------
        filename : PathLike
            Path to a bathymetry file, e.g. mbth_wb1.csv

        Returns
        -------
        Self
            The segment metadata and the bathymetry data
        """
        if Path(filename).suffix != ".csv":
            raise NotImplementedError

        with open(filename) as f:
            lines = f.readlines()

        # The first 7 lines are file headings and segment data.
        # Extract the comment, if any
        matched = re.match(r"\$(.*),", lines[0])
        if matched:
            comment = matched.group(0)
        else:
            comment = None

        # Read the segment data from the next 5 rows. The first of these lines SHOULD
        # contain
        #
        #       Seg, followed by a header for each model segment, this is ignored
        #
        # according to the manual, but in practice I don't see 'Seg' appearing in any of
        # the bathymetry files so we manually replace it here.
        #
        # Also drop any nan-valued rows, they arise from superfluous comma separators at
        # the end of rows.
        segment_data = (
            pd.read_csv(
                StringIO("\n".join(lines[1:6])),
                index_col=False,
            )
            .rename(columns={"Unnamed: 0": "SEG"})
            .transpose()
            .dropna(axis=0, how="any")
            .reset_index()
        )
        segment_data.columns = segment_data.iloc[0]
        segment_data = segment_data.iloc[1:]

        # Add some missing units
        segment_data = segment_data.rename(
            columns={
                "DLX": "DLX [m]",
                "ELWS": "ELWS [m]",
                "PHI0": "PHI0 [rad]",
            }
        )

        # 7th line: titles that are ignored by the model.
        # Not sure if the placement of any of these has any significance, so we just
        # keep everything here
        ignored = lines[6].strip().split(",")

        # (From the manual) 8th line to end of file:
        #
        #   1st column is layer height in m
        #   2nd column are segment widths in m for segment 1,
        #   3rd column are segment widths in m for segment 2, etc.
        #
        # Note that the segment widths for the first segment and last segment are 0 and
        # for the top layer K=1 and bottom layer are also 0. On the far right-hand side
        # there is a layer # specification.
        data = pd.read_csv(
            StringIO("\n".join(lines[7:])),
            index_col=False,
            header=None,
        )

        # There's an extra comma delimeter at the end of each column which results in a
        # phantom column, so we drop that extra column here
        data = data.drop(columns=data.columns[-1])

        # Rename and reorder the columns to make more sense
        nsegments = len(data.columns) - 2
        data.columns = (
            ["Layer height [m]"]
            + [f"Width (segment {i + 1}) [m]" for i in range(nsegments)]
            + ["Layer #"]
        )
        data = data[["Layer #", "Layer height [m]"] + data.columns[1:-1].to_list()]

        return cls(
            filename=filename,
            segment_data=segment_data,
            comment=comment,
            ignored=ignored,
            data=data,
        )


@dataclass
class Temperature(BaseData):
    """A container for temperature data."""

    comment: str
    do: pd.DataFrame
    profile_file: str | None
    tds: pd.DataFrame
    temperc: pd.DataFrame
    filename: PathLike | None = None

    @classmethod
    def from_file(cls, filename: PathLike) -> Self:
        """Parse a temperature profile file.

        Parameters
        ----------
        filename : PathLike
            Path to a temperature profile file, e.g. mvpr1.npt

        Returns
        -------
        Self
            The temperature profile, total dissolved solids, and dissolved oxygen
        """
        if Path(filename).suffix != ".npt":
            raise NotImplementedError

        profile_file = None
        comment = None

        with open(filename) as f:
            lines = f.readlines()

        if len(lines) < 2:
            raise ValueError(
                f"{filename} doesn't appear to have temperature data. Aborting."
            )

        try:
            # First line is a header containing the name of a profile file
            matched = re.match(r"^Profile file: (?P<fname>[^\s]+)$", lines[0])
            if matched:
                profile_file = matched.group("fname")
            else:
                warnings.warn(
                    (
                        "Cannot determine profile file name used to create the "
                        "temperature profile"
                    ),
                    category=DeprecationWarning,
                    stacklevel=1,
                )

            # Second line is a comment describing something about how the temperature
            # profile was created
            comment = lines[1]

            # Next there are three blocks of temperature, dissolved solids, and
            # dissolved oxygen data
            start, end = _get_next_block_idx(lines, 2, "TemperC")
            temperc = _lines_to_df(lines[start:end])

            start, end = _get_next_block_idx(lines, end, "TDS")
            tds = _lines_to_df(lines[start:end])

            start, end = _get_next_block_idx(lines, end, "DO")
            do = _lines_to_df(lines[start:end])
        except Exception as e:
            raise ValueError(f"Failed to parse temperature profile: {filename}.") from e

        return cls(
            filename=filename,
            temperc=temperc,
            tds=tds,
            do=do,
            comment=comment,
            profile_file=profile_file,
        )


def _lines_to_df(lines: list[str]) -> pd.DataFrame:
    """Convert a set of temperature profile lines into a DataFrame.

    Parameters
    ----------
    lines : list[str]
        A list of lines from a temperature profile file containing a
        whitespace-separated block of data

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the data block
    """
    return pd.read_csv(
        StringIO("\n".join(lines[1:])),
        sep=r"\s+",
        header=None,
    )


def _get_next_block_idx(lines: list[str], start: int, search: str) -> tuple[int, int]:
    """Get the next data block's indices from the lines of a temperature profile file.

    Temperature profile files have blocks of data that look like this:

    TemperC       T1      T1      T1      T1      T1      T1      T1      T1      T1
               20.75   20.35   20.04   19.93   19.74   18.58   15.19   14.32    13.7
               13.16   12.96    12.8   12.65   12.52   12.39   12.27   12.15   12.02
                11.9   11.78   11.66   11.56   11.49   11.42   11.35   11.28   11.19
               ...

    TDS mgl       C1      C1      C1      C1      C1      C1      C1      C1      C1
                32.0    32.0    32.0    32.0    32.0   31.79    30.8    29.5   28.19
               27.11    27.0    27.0   27.02   27.29   27.64   27.99   28.32   28.65
               28.98   29.34    29.7   30.12    30.7   31.29   31.86    32.0    32.0
               ...

    DO mgl        C2      C2      C2      C2      C2      C2      C2      C2      C2
                9.83    9.87    9.94    9.98    9.97    9.97   10.11   10.12   10.13
                 9.9    9.88    9.87    9.85    9.84    9.83    9.82    9.81    9.79
                9.78    9.75    9.72    9.69    9.65    9.58     9.5    9.44     9.4

    This function grabs the line indices containing the next block of data.


    Parameters
    ----------
    lines : list[str]
        Lines read from a temperature profile file
    start : int
        Starting index to search
    search : str
        Text that the next block of data should start with

    Returns
    -------
    tuple[int, int]
        Starting and ending indices of the next block
    """
    for i in range(start, len(lines)):
        if lines[i].startswith(search):
            for j in range(i, len(lines)):
                if lines[j].strip() == "":
                    return i, j

            # End of file may not have a blank line
            return i, len(lines) + 1

    raise ValueError("Never found the search term.")
