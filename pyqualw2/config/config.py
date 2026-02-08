from os import PathLike
from pathlib import Path
from typing import Self

import pandas as pd

from .inputs import BathymetryInput, ProfileInput


class Config:
    """A container that holds all configuration data for a simulation."""

    def __init__(
        self,
        con: PathLike,
        bathymetry: BathymetryInput,
        temperature: ProfileInput,
    ):
        self.con = con
        self.bathymetry = bathymetry
        self.temperature = temperature

    @classmethod
    def from_csv(
        cls,
        con: PathLike,
        bathymetry: PathLike,
        temperature: PathLike,
    ) -> Self:
        """Generate a Config from w2_con, bathymetry, and temperature CSV files.

        Parameters
        ----------
        con : PathLike
            Path to a w2_con.csv
        bathymetry : PathLike
            Path to the bathymetry file, e.g. mbth_wb1.csv
        temperature : PathLike
            Path to the temperature file, e.g. mvpr1.csv

        Returns
        -------
        Self
            A Config instance containing all the information needed to run a simulation
        """
        return cls(
            con=con,
            bathymetry=BathymetryInput.from_file(bathymetry),
            temperature=ProfileInput.from_file(temperature),
        )

    @classmethod
    def from_settings(cls, settings: PathLike) -> Self:
        """Generate a Config from a settings.toml file.

        Parameters
        ----------
        settings : PathLike
            Path to a settings.toml file

        Returns
        -------
        Self
            A config instance containing all the information needed to run a simulation

        """
        raise NotImplementedError

    @staticmethod
    def parse_bathymetry(file: PathLike) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Parse a bathymetry file.

        Parameters
        ----------
        file : PathLike
            Path to a bathymetry file, e.g. mbth_wb1.csv

        Returns
        -------
        tuple[pd.DataFrame, pd.DataFrame]
            The segment metadata and the bathymetry data
        """
        if Path(file).suffix != ".csv":
            raise NotImplementedError

        # Segment metadata. Ignore first two lines:
        # $Millerton Bathymetry,,,,,,,,,,,...
        # ,1,2,3,4,5,6,7,8,9,10,11,12,13,...
        #
        # but read the next 4 rows, which give per-segment DLX, ELWS, PHI0, and FRIC
        segments = pd.read_csv(file, index_col=False, skiprows=2, nrows=4, header=None)

        # The values are stored in columns; transpose and update the column names
        segments = segments.transpose().drop(index=segments.columns[-1]).reset_index()
        segments.columns = segments.iloc[0]
        segments = segments.iloc[1:]

        data = pd.read_csv(file, index_col=False, skiprows=7, header=None)
        data.columns = [f"Layer {i}" for i in range(len(data.columns - 2))] + [
            "K",
            "ELEV",
        ]

        return (segments, data)
