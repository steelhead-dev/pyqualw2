import re
import warnings
from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass
from io import StringIO
from os import PathLike
from pathlib import Path
from typing import ClassVar, Self

import pandas as pd


class BaseInput(ABC):
    """Base class for all input data types."""

    @classmethod
    @abstractmethod
    def from_file(cls, filename: PathLike | str) -> Self:
        """Parse a data file to a python object.

        Parameters
        ----------
        filename : PathLike | str
            Path to the data file

        Returns
        -------
        Self
            An object containing the data from the file
        """

    @abstractmethod
    def to_file(
        self,
        filename: PathLike | str,
        overwrite: bool = False,
        create_parents: bool = False,
    ):
        """Serialize the config to a file.

        Parameters
        ----------
        filename : PathLike | str
            Path where the data should be written
        overwrite : bool
            If True, overwrite an existing file
        create_parents : bool
            If True, create any necessary parent directories
        """


@dataclass
class BathymetryInput(BaseInput):
    """Container for bathymetry input data."""

    data: pd.DataFrame
    segment_data: pd.DataFrame
    ignored: list[str]
    filename: PathLike | str | None = None
    comment: str | None = None

    # This mapping defines human readable mappings that are used to relabel the input
    # bathymetry file segment data columns. The inverse mapping is used when writing
    # bathymetry to a csv for use by qualw2.
    _segment_data_column_map: ClassVar[dict[str, str]] = {
        "DLX": "DLX [m]",
        "ELWS": "ELWS [m]",
        "PHI0": "PHI0 [rad]",
    }

    @classmethod
    def _ingest_segment_data(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the raw segment data.

        - Renames the (empty) first column name
        - Transposes the data to be columnar
        - Add in missing units
        - Dropping nan-valued columns

        Returns
        -------
        pd.DataFrame
            The segment_data, transformed to a columnar format and with better column
            names
        """
        segment_data = (
            df.rename(columns={"Unnamed: 0": "SEG"})
            .transpose()
            .dropna(axis=0, how="any")
            .reset_index()
        )
        segment_data.columns = segment_data.iloc[0]
        segment_data = segment_data.iloc[1:]
        return segment_data.rename(columns=cls._segment_data_column_map)

    @classmethod
    def _format_export_segment_data(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Format the segment data for export to csv.

        Inverse operation of `_ingest_segment_data`.

        Parameters
        ----------
        df : pd.DataFrame
            The segment data to be transformed

        Returns
        -------
        pd.DataFrame
            The segment data, transformed to row-wise format and with qualw2-compatible
            column names
        """
        return df.rename(
            columns={
                col: raw_col for raw_col, col in cls._segment_data_column_map.items()
            }
        ).transpose()

    @staticmethod
    def _ingest_data(df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the raw bathymetry data.

        - Drop the last column, it's only there because of superfluous ',' separators
        - Reorder and label the columns for human readability

        Parameters
        ----------
        df : pd.DataFrame
            Data read from the bathymetry file. From the manual, this should be:

              1st column: layer height in m
              2nd column: segment widths in m for segment 1
              3rd column: segment widths in m for segment 2
              ...

            Note that the segment widths for the first segment and last segment are 0
            and for the top layer K=1 and bottom layer are also 0. On the far right-hand
            side there is a layer # specification.

        Returns
        -------
        pd.DataFrame
            The preprocessed bathymetry
        """
        # There's an extra comma delimeter at the end of each column which results in a
        # phantom column, so we drop that extra column here
        df = df.drop(columns=df.columns[-1])

        # Rename and reorder the columns to make more sense
        nsegments = len(df.columns) - 2
        df.columns = (
            ["Layer height [m]"]
            + [f"Width (segment {i + 1}) [m]" for i in range(nsegments)]
            + ["Layer #"]
        )

        col_height, *col_widths, col_number = df.columns
        return df[[col_number, col_height, *col_widths]]

    @staticmethod
    def _format_export_data(df: pd.DataFrame) -> pd.DataFrame:
        """Format the bathymetry data for export to csv.

        Inverse operation of `_ingest_data`.

        Parameters
        ----------
        df : pd.DataFrame
            Data to be exported

        Returns
        -------
        pd.DataFrame
            Formatted data ready for export to csv
        """
        col_number, col_height, *col_widths = df.columns
        return df[[col_height, *col_widths, col_number]]

    @classmethod
    def from_file(cls, filename: PathLike | str) -> Self:
        """Parse a bathymetry file.

        Parameters
        ----------
        filename : PathLike | str
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
        #       SEG, followed by a header for each model segment, this is ignored
        #
        # according to the manual, but in practice I don't see 'SEG' appearing in any of
        # the bathymetry files so we manually replace it here.
        #
        # Also drop any nan-valued rows, they arise from superfluous comma separators at
        # the end of rows.
        segment_data = cls._ingest_segment_data(
            pd.read_csv(
                StringIO("\n".join(lines[1:6])),
                index_col=False,
            )
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
        data = cls._ingest_data(
            pd.read_csv(
                StringIO("\n".join(lines[7:])),
                index_col=False,
                header=None,
            )
        )

        return cls(
            filename=filename,
            segment_data=segment_data,
            comment=comment,
            ignored=ignored,
            data=data,
        )

    def to_file(
        self,
        filename: PathLike | str = "mbth.csv",
        overwrite: bool = False,
        create_parents: bool = False,
    ):
        """Serialize the config to a csv file.

        Parameters
        ----------
        filename : PathLike | str
            Path where the data should be written
        overwrite : bool
            If True, overwrite an existing file
        create_parents : bool
            If True, create any necessary parent directories
        """
        path = Path(filename)
        if path.suffix != ".csv":
            raise NotImplementedError

        _create_parents_or_fail(path, overwrite, create_parents)

        with open(path, "w") as f:
            f.write(f"{self.comment if self.comment else ''}\n")
            self._format_export_segment_data(self.segment_data).to_csv(
                f, sep=",", header=None
            )
            f.write(",".join(self.ignored) + "\n")
            self._format_export_data(self.data).to_csv(
                f, sep=",", index=False, header=None
            )


@dataclass
class ProfileInput(BaseInput):
    """A container for profile (layer-dependent) input data."""

    comment: str
    data: pd.DataFrame
    profile_file: str | None
    filename: PathLike | str | None = None

    @classmethod
    def from_file(cls, filename: PathLike | str) -> Self:
        """Parse a profile file.

        Profile files contain layer-dependent quantities, such as temperature,
        dissolved oxygen, or total dissolved solids.

        Parameters
        ----------
        filename : PathLike | str
            Path to a profile file, e.g. mvpr1.npt

        Returns
        -------
        Self
            An object containing the layer-dependent quantities from a profile file
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
            comment = lines[1].strip()
            lines = lines[2:]

            data = {}
            for name, df in cls._iter_blocks(lines):
                data[name] = df

        except Exception as e:
            raise ValueError(f"Failed to parse temperature profile: {filename}.") from e

        return cls(
            filename=filename,
            data=pd.DataFrame(data=data),
            comment=comment,
            profile_file=profile_file,
        )

    @staticmethod
    def _iter_blocks(
        lines: list[str],
    ) -> Generator[tuple[str, pd.DataFrame]]:
        """Iterate through the data blocks in a profile data file.

        Profile files have blocks of data that look like this:

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

        This function grabs the next block of data.

        Parameters
        ----------
        lines : list[str]
            Lines from a profile file. Data is assumed to start on lines[0], or lines[1]
            if the current line is empty

        Returns
        -------
        Generator[tuple[str, np.NDArray]]
            Tuples of dataset name and 1-D array of layer-dependent data
        """
        while lines:
            i = 0

            if lines[0].strip() == "":
                i += 1

            if not lines[i:]:
                return None

            split = re.split(r"\s+", lines[i].strip())
            if not split:
                raise ValueError("Unable to extract name of data from profile file")

            # iterate backwards through the split line seeking the first "word" (which
            # may have spaces...)
            name = None
            word = None
            for j in range(len(split) - 1, -1, -1):
                if word is None:
                    word = split[j]
                elif split[j] != word:
                    name = " ".join(split[: j + 1])
                    i += 1
                    break

            if name is None:
                raise ValueError("Unable to extract name of data from profile block")

            joined = StringIO()
            for line in lines[i:]:
                i += 1

                # An empty line indicates the end of the current block of data
                if line.strip() == "":
                    break

                joined.write(f"{line.strip()}\n")

            lines = lines[i:]

            # Need to reset the file pointer to the beginning for read_csv
            joined.seek(0)
            data = (
                pd.read_csv(joined, sep=r"\s+", header=None, index_col=False)
                .to_numpy()
                .flatten()
            )
            yield name, data

    def to_file(
        self,
        filename: PathLike | str = "mvpr1.npt",
        overwrite: bool = False,
        create_parents: bool = False,
    ):
        """Serialize the profile file to a file on disk.

        Parameters
        ----------
        filename : PathLike | str
            Path where the data should be written
        overwrite : bool
            If True, overwrite an existing file
        create_parents : bool
            If True, create any necessary parent directories
        """
        path = Path(filename)
        if path.suffix != ".npt":
            raise NotImplementedError

        _create_parents_or_fail(path, overwrite, create_parents)

        lines = [
            f"Profile file: {self.profile_file if self.profile_file else None}",
            self.comment,
        ]
        for name, arr in self.data.items():
            label = self._get_label(name)

            # Make the "column" headers
            lines.append(f"{name:8}" + "".join(f"{label:>8}" for _ in range(9)))

            # Write the data in 9 "columns", wrapping as needed to print all the data
            for row in arr.to_numpy().reshape((-1, 9)):
                lines.append("        " + "".join(f"{val:>8.2f}" for val in row))
            lines.append("")

        with open(path, "w") as f:
            f.write("\n".join(lines))

    @staticmethod
    def _get_label(name: str) -> str:
        """Get the "column" label for a layer-dependent quantity.

        Parameters
        ----------
        name : str
            Name of the layer-dependent quantity

        Returns
        -------
        str
            "Column" label to use when writing to a .npt profile file
        """
        low = name.lower()
        if low.startswith("temp"):
            return "T1"
        elif low.startswith("tds"):
            return "C1"
        elif low.startswith("do"):
            return "C2"
        else:
            raise NotImplementedError


@dataclass
class W2ConSimpleInput(BaseInput):
    """A simple parser for the main qualw2 configuration file.

    Note that this class does not parse the entire file - it only allows users to read
    and modify TMSTRT, TMEND, and YEAR values.
    """

    filename: PathLike | str
    content: str
    time_lineno: int

    @classmethod
    def from_file(cls, filename: PathLike | str) -> Self:
        """Parse a qualw2 config file.

        Parameters
        ----------
        filename : PathLike | str
            Path to a qualw2 config file, e.g. w2_con.csv

        Returns
        -------
        Self
            A simple object wrapping the content of a w2_con.csv file
        """
        if Path(filename).suffix != ".csv":
            raise NotImplementedError

        with open(filename) as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith("TMSTRT"):
                return cls(
                    filename=filename,
                    content="".join(lines),
                    time_lineno=i + 1,
                )

        raise ValueError(f"Unable to find the time card in {filename}")

    def to_file(
        self,
        filename: PathLike | str = "w2_con.csv",
        overwrite: bool = False,
        create_parents: bool = False,
    ):
        """Serialize the config to a csv file.

        Parameters
        ----------
        filename : PathLike | str
            Path where the data should be written
        overwrite : bool
            If True, overwrite an existing file
        create_parents : bool
            If True, create any necessary parent directories
        """
        path = Path(filename)
        if path.suffix != ".csv":
            raise NotImplementedError

        _create_parents_or_fail(path, overwrite, create_parents)
        with open(path, "w") as f:
            f.write(self.content)

    @property
    def timedata(self) -> tuple[float, float, int]:
        """Get the TMSTRT, TMEND, and YEAR values for the configuration.

        Returns
        -------
        tuple[float, float, int]
            TMSTRT, TMEND, and YEAR values for the configuration
        """
        lines = self.content.splitlines(keepends=True)
        tmstart, tmend, year, *rest = lines[self.time_lineno].split(",")
        return float(tmstart), float(tmend), int(year)

    @timedata.setter
    def timedata(self, value: tuple[float, float, int]):
        """Set the TMSTRT, TMEND, and YEAR values for the configuration.

        Parameters
        ----------
        value : tuple[float, float, int]
            A tuple of TMSTRT, TMEND, and YEAR to set
        """
        tmstart, tmend, year = value
        lines = self.content.splitlines(keepends=True)
        _, _, _, *rest = lines[self.time_lineno].split(",")
        lines[self.time_lineno] = ",".join([str(tmstart), str(tmend), str(year), *rest])
        self.content = "".join(lines)


def _create_parents_or_fail(
    path: PathLike,
    overwrite: bool = False,
    create_parents: bool = True,
):
    path = Path(path)
    if path.exists():
        if not overwrite:
            raise OSError(
                f"Cannot write file to {path}; a file already exists there. To "
                "overwrite it, pass `overwrite=True`."
            )
    else:
        if not path.parent.exists():
            if create_parents:
                path.parent.mkdir(parents=True, exist_ok=True)
            else:
                raise OSError(
                    f"Parent directory {path.parent} does not exist. Aborting. "
                    "To create the parent directory, pass `create_parents=True`."
                )
