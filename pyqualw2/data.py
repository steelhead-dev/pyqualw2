import re
import warnings
from abc import ABC, abstractmethod
from io import StringIO
from os import PathLike
from pathlib import Path
from typing import Self

import numpy as np
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


class Bathymetry(BaseData):
    """Container for Bathymetry data."""

    def __init__(
        self,
        dlx: np.array,
        elws: np.array,
        phi0: np.array,
        fric: np.array,
        data: pd.DataFrame,
        file: PathLike | None = None,
    ):
        self.file = file
        self.dlx = dlx
        self.elws = elws
        self.phi0 = phi0
        self.fric = fric
        self.data = data

    @classmethod
    def from_file(cls, file: PathLike) -> Self:
        """Parse a bathymetry file.

        Parameters
        ----------
        file : PathLike
            Path to a bathymetry file, e.g. mbth_wb1.csv

        Returns
        -------
        Self
            The segment metadata and the bathymetry data
        """
        if Path(file).suffix != ".csv":
            raise NotImplementedError

        # Segment metadata. Ignore first two lines:
        # $Millerton Bathymetry,,,,,,,,,,,...
        # ,1,2,3,4,5,6,7,8,9,10,11,12,13,...
        #
        # but read the next 4 rows, which give per-segment DLX, ELWS, PHI0, and FRIC.
        # The values are stored in columns; transpose and update the column names.
        segments = pd.read_csv(file, index_col=False, skiprows=2, nrows=4, header=None)
        segments = segments.transpose().drop(index=segments.columns[-1]).reset_index()
        segments.columns = segments.iloc[0]
        segments = segments.iloc[1:]

        # Finally, read the rest of the file to get the bathymetry data
        data = pd.read_csv(file, index_col=False, skiprows=7, header=None)
        data.columns = [f"Layer {i}" for i in range(len(data.columns - 2))] + [
            "K",
            "ELEV",
        ]

        return cls(
            file=file,
            dlx=segments["DLX"].to_numpy(),
            elws=segments["ELWS"].to_numpy(),
            phi0=segments["PHI0"].to_numpy(),
            fric=segments["FRIC"].to_numpy(),
            data=data,
        )


class Temperature(BaseData):
    """A container for temperature data."""

    def __init__(
        self,
        temperc: pd.DataFrame,
        tds: pd.DataFrame,
        do: pd.DataFrame,
        profile_file: str | None,
        file: PathLike,
        comment: str,
    ):
        self.file = file
        self.tds = tds
        self.temperc = temperc
        self.do = do
        self.comment = comment
        self.profile_file = profile_file

    @classmethod
    def from_file(cls, file: PathLike) -> Self:
        """Parse a temperature profile file.

        Parameters
        ----------
        file : PathLike
            Path to a temperature profile file, e.g. mvpr1.npt

        Returns
        -------
        Self
            The temperature profile, total dissolved solids, and dissolved oxygen
        """
        if Path(file).suffix != ".npt":
            raise NotImplementedError

        profile_file = None
        comment = None

        with open(file) as f:
            lines = f.readlines()

        if len(lines) < 2:
            raise ValueError(
                f"{file} doesn't appear to have temperature data. Aborting."
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
            raise ValueError(f"Failed to parse temperature profile: {file}.") from e

        return cls(
            file=file,
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
