from os import PathLike
from typing import Self

from .inputs import BathymetryInput, ProfileInput, W2ConSimpleInput


class Config:
    """A container that holds all configuration data for a simulation."""

    def __init__(
        self,
        con: W2ConSimpleInput,
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
            Path to a qualw2 configuration file, e.g. w2_con.csv
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
            con=W2ConSimpleInput.from_file(con),
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
