import warnings
from collections import defaultdict
from textwrap import indent
from typing import Any, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .options import (
    AZC,
    DYNGTC,
    FRICC,
    GRIDC,
    ICEC,
    SINKC,
    SLHTC,
    SLICEC,
    SLTRC,
    WTYPEC,
    ImplicitExplicit,
    InflowEntryType,
    WithdrawalType,
)

type ParseResult = tuple[Self, int]


class ParseError(Exception):
    def __init__(self, lines, lineno, message=""):
        nlines = len(lines)
        snippet = (
            indent(
                "".join(lines[max(0, lineno - 10) : min(nlines, lineno)]),
                prefix="    ",
            )
            + indent(
                lines[lineno],
                prefix="--> ",
            )
            + indent(
                "".join(lines[min(nlines, lineno + 1) : min(nlines, lineno + 10)]),
                prefix="    ",
            )
        )
        super().__init__(
            f"Problem parsing line {lineno}: {message}\n\n{snippet}",
        )


class SubConfig(BaseSettings):
    """A container for 'configuration cards', i.e. subsections, of w2_con.csv.

    Child subclasses may contain aliases for certain fields when there is an
    inconsistency between the documentation and what w2_con.csv actually contains.
    """

    model_config = SettingsConfigDict(extra="ignore", env_prefix="PYQUALW2_")

    @model_validator(mode="before")
    @classmethod
    def validate(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Warn the user if any extra arguments are passed to the model.

        Parameters
        ----------
        values : dict[str, Any]
            Kwargs passed to the model

        Returns
        -------
        dict[str, Any]
            Kwargs passed to the model
        """
        fields = set()
        aliases = set()
        for field, info in cls.model_fields.items():
            fields.add(field)
            if info.alias is not None:
                aliases.add(info.alias)

        extras = set(values.keys()) - fields - aliases
        if extras:
            warnings.warn(
                f"Extra fields passed to {cls.__name__}: {extras}", stacklevel=1
            )
        return values

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        pass

    @classmethod
    def parse_line_pair_table(cls, lines: list[str], i: int) -> ParseResult:
        """Parse a pair of lines that form a table of attributes.

        For example, if `lines` contains

            NWB, NBR, IMX, KMX, NPROC, CLOSEC,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
            1,4,46,212,1,OFF     ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
             ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

        then `SubConfig.parse_line_pair_table(lines, i)` will generate a dictionary

            {
                "nwb": "1",
                "nbr": "4",
                "imx": "46",
                "kmx": "212",
                "nproc": "1",
                "closec": "off",
            }

        and attempt to instantiate a SubConfig with this dict passed in as kwargs.

        Parameters
        ----------
        lines : list[str]
            List of lines to ingest; only the first 3 will be consumed

        Returns
        -------
        ParseResult
            A SubConfig subclass instance, and remaining unparsed lines from the config
        """
        kwargs = {}
        for key, value in zip(
            lines[i].split(","), lines[i + 1].split(","), strict=True
        ):
            if key != "" and value != "":
                kwargs[key.strip().lower()] = value.strip()
            else:
                break

        try:
            return cls(**kwargs), i + 3
        except Exception as e:
            raise ParseError(lines, i) from e

    @classmethod
    def parse_row_variables(cls, lines: list[str], i: int) -> ParseResult:
        """Parse a matrix of values into one or more lists of values.

        Each column represents some configuration object. For example, consider the
        BranchGeometry section:

            BR1,BR2,BR3,BR4,BR5,BR6,BR7,BR8,BR9,BR10,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
            2,34,39,44,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
            31,36,41,45,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
            0,0,0,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
            0,21,27,28,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
            1,1,1,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
            0,0,0,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
            0,0,0,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
             ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

        In this subsection, each column represents a separate branch representing a
        sloping river section that is linked in series. Each row corresponds to a
        separate configuration variable for the branch, so in the example above there
        are 4 branches. The first branch has values

            US: 2
            DS: 31
            UHS: 0
            DHS: 0
            NLMIN: 1
            SLOPE: 0
            SLOPEC: 0

        And so on for the other branches.

        Parameters
        ----------
        lines : list[str]
            The lines to ingest

        Returns
        -------
        ParseResult
            A SubConfig subclass instance, and the remaining lines from the config

        """
        fields = list(cls.model_fields.keys())

        j = 0
        kwargs = defaultdict(list)
        for line in lines[i + 1 :]:
            split = line.strip().split(",")
            if split[0] == "":
                # Hit an empty line, signifying the end of a configuration block
                break

            for value in split:
                value = value.strip()
                if value == "":
                    # Hit the end of the data in a line. Continue to the next line
                    break

                if j < len(fields):
                    kwargs[fields[j]].append(value)
                else:
                    warnings.warn(
                        (
                            "Encountered more configuration settings than there are "
                            f"expected fields on line {j + i + 1}. Skipping."
                        ),
                        stacklevel=1,
                    )
                    break

            j += 1

        # Skip one line for each line consumed, one line for the section header, and one
        # for the empty line after the section
        try:
            return cls(**kwargs), j + i + 2
        except Exception as e:
            raise ParseError(lines, i) from e

    def __contains__(self, name: str) -> bool:
        """Return true if the given name exists as an attribute on the class.

        Parameters
        ----------
        name : str
            Name of a w2_con option

        Returns
        -------
        bool
            True if the subsection has the option, False otherwise
        """
        return name in self.__class__.model_fields


class Title(SubConfig):
    title: str

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls(title="\n".join(lines[i : i + 10])), i + 12


class GridDimensions(SubConfig):
    nwb: int
    nbr: int
    imx: int
    kmx: int
    nproc: int
    closec: bool

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_line_pair_table(lines, i)


class InflowOutflowDimensions(SubConfig):
    ntr: int
    nst: int
    niw: int
    nwd: int
    ngt: int
    nsp: int
    npi: int
    npu: int

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_line_pair_table(lines, i)


class Constituents(SubConfig):
    ngc: int
    nss: int
    nal: int
    nep: int
    nbod: int
    nmc: int
    nzp: int

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_line_pair_table(lines, i)


class Miscellaneous(SubConfig):
    nday: int
    selectc: str
    habtatc: bool
    envirpc: bool
    aeratec: bool
    inituwl: bool
    orcc: bool = Field(alias="orgcc")
    sed_diag: bool

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_line_pair_table(lines, i)


class TimeControl(SubConfig):
    tmstrt: float
    tmend: float
    year: int

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_line_pair_table(lines, i)


class TimestepControl(SubConfig):
    ndt: int = Field(alias="ndlt")
    dltmin: float
    dltintr: bool = Field(alias="dltinter")

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_line_pair_table(lines, i)


class TimestepDate(SubConfig):
    dltd: list[float]

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class MaximumTimestep(SubConfig):
    dltmax: list[float]

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class TimestepFraction(SubConfig):
    dltf: list[float]

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class TimestepLimitations(SubConfig):
    visc: list[bool]
    celc: list[bool]
    dltadd: list[bool]

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class BranchGeometry(SubConfig):
    us: list[int]
    ds: list[int]
    uhs: list[int]
    dhs: list[int]
    nlmin: list[int]
    slope: list[float]
    slopec: list[float]

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class WaterbodyDefinition(SubConfig):
    lat: list[float]
    long: list[float]
    ebot: list[float]
    bs: list[int]
    be: list[int]
    jbdn: list[int]

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class InitialConditions(SubConfig):
    t2i: list[float]
    icethi: list[float]
    wtypec: list[WTYPEC]
    gridc: list[GRIDC]

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class Calculations(SubConfig):
    vbc: list[bool]  # True
    ebc: list[bool]  # True
    mbc: list[bool]  # True
    pqc: list[bool]  # False
    evc: list[bool]  # True
    prc: list[bool]  # False

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class DeadSea(SubConfig):
    windc: list[bool]  # True
    qinc: list[bool]  # True
    qoutc: list[bool]  # True
    heatc: list[bool]  # True

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class Interpolation(SubConfig):
    qinic: list[bool]  # True
    dtric: list[bool]  # True
    hdic: list[bool]  # True

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class HeatExchange(SubConfig):
    slhtc: list[SLHTC]  # SLHTC.TERM
    sroc: list[bool]  # False
    rhevap: list[bool]  # False
    metic: list[bool]  # True
    fetchc: list[bool]  # False
    afw: list[float]  # 9.2
    bfw: list[float]  # 0.46
    cfw: list[float]  # 2.0
    windh: list[float]

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class IceCover(SubConfig):
    icec: list[ICEC]  # ICEC.OFF
    slicec: list[SLICEC]  # SLICEC.DETAIL
    albedo: list[float]  # 0.25
    hwi: list[float]  # 10.0
    betai: list[float]  # 0.6
    gammai: list[float]  # 0.07
    icemin: list[float]  # 0.05
    icet2: list[float]  # 3.0

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class TransportScheme(SubConfig):
    sltrc: list[SLTRC]  # SLTRC.ULTIMATE
    theta: list[float]  # 0.55

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class HydraulicCoefficients(SubConfig):
    ax: list[float]  # 1.0
    dx: list[float]  # 1.0
    cbhe: list[float]  # 0.3
    tsed: list[float]
    fi: list[float]  # 0.01
    tsedf: list[float]  # 1.0
    fricc: list[FRICC]  # FRICC.CHEZY
    z0: list[float]  # 0.001

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class VerticalEddyViscosity(SubConfig):
    azc: list[AZC]  # AZC.TKE
    azslc: list[ImplicitExplicit]  # AZSLC.IMP
    azmax: list[float]  # 1.0
    fbc: list[int]  # 3
    e: list[float]  # 9.535
    arodi: list[float]  # 0.431
    strcklr: list[float]  # 24.0
    boundfr: list[float]  # 10.0
    tkecal: list[ImplicitExplicit]  # TKECAL.IMP

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class NumberOfStructures(SubConfig):
    nstr: list[int]
    dynstruc: list[bool]

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


class StructureInterpolation(SubConfig):
    stric: list[bool]  # False

    @classmethod
    def parse(cls, lines: list[str], i: int) -> ParseResult:
        return cls.parse_row_variables(lines, i)


# class Structure top selective withdrawal limit(SubConfig):
#     ktstr: int
#
#
# class Structure bottom selective withdrawal liimit(SubConfig):
#     kbstr: int
#
#
# class Sink type(SubConfig):
#     sinkc: SINKC # SINKC.POINT
#
#
# class Structure elevation(SubConfig):
#     estr: float
#
#
# class Structure width(SubConfig):
#     wstr: float
#
#
# class Pipes(SubConfig):
#     iupi: int
#     idpi: int
#     eupi: float
#     edpi: float
#     wpi: float
#     dlxpi: float
#     fpi: float
#     fminpi: float
#     latpic: WithdrawalType
#     dynpipe: bool
#
#
# class Upstream pipe(SubConfig):
#     pupic: InflowEntryType # InflowEntryType.DISTR
#     etupi: float
#     ebupi: float
#     ktupi: int
#     kbupi: int
#
#
# class Downstream pipe(SubConfig):
#     pdpic: InflowEntryType # InflowEntryType.DISTR
#     etdpi: float
#     ebdpi: float
#     ktdpi: int
#     kbdpi: int
#
#
# class Spillways(SubConfig):
#     iusp: int
#     idsp: int
#     esp: float
#     a1sp: float
#     b1sp: float
#     a2sp: float
#     b2sp: float
#     latspc: WithdrawalType
#
#
# class Upstream spillways(SubConfig):
#     puspc: InflowEntryType # InflowEntryType.DISTR
#     etusp: float
#     ebusp: float
#     ktusp: int
#     kbusp: int
#
#
# class Downstream spillways(SubConfig):
#     pdspc: InflowEntryType # InflowEntryType.DISTR
#     etdsp: float
#     ebdsp: float
#     ktdsp: int
#     kbdsp: int
#
#
# class Spillway dissolved gas(SubConfig):
#     gasspc: bool # False
#     eqsp: int
#     asp: float
#     bsp: float
#     csp: float
#
#
# class Gates(SubConfig):
#     iugt: int
#     idgt: int
#     egt: float
#     a1gt: float
#     b1gt: float
#     g1gt: float
#     a2gt: float
#     b2gt: float
#     g2gt: float
#     latgtc: WithdrawalType
#
#
# class Gate weir(SubConfig):
#     ga1: float
#     gb1: float
#     ga2: float
#     gb2: float
#     dyngtc: DYNGTC
#     gtic: bool
#
#
# class Upstream gate(SubConfig):
#     pugtc: InflowEntryType # InflowEntryType.DISTR
#     etugt: float
#     ebugt: float
#     ktugt: int
#     kbugt: int
#
#
# class Downstream gate(SubConfig):
#     pdgtc: InflowEntryType # InflowEntryType.DISTR
#     etdgt: float
#     ebdgt: float
#     ktdgt: int
#     kbdgt: int
#
#
# class Gate dissolved gas(SubConfig):
#     gasgtc: bool # False
#     eqgt: int
#     agasgt: float
#     bgasgt: float
#     cgasgt: float
#
#
# class Pumps 1(SubConfig):
#     iupu: int
#     idpu: int
#     epu: float
#     strtpu: float
#     endpu: float
#     eonpu: float
#     eoffpu: float
#     qpu: float
#     latpuc: WithdrawalType # WithdrawalType.DOWN
#     dynpump: bool # False
#
#
# class Pumps 2(SubConfig):
#     ppuc: InflowEntryType # InflowEntryType.DISTR
#     etpu: float
#     ebpu: float
#     ktpu: int
#     kbpu: int
#
#
# class Internal weir segment location(SubConfig):
#     iwr: int
#
#
# class Internal weir top layer(SubConfig):
#     ektwr: float
#
#
# class Internal weir bottom layer(SubConfig):
#     ekbwr: float
#
#
# class Withdrawal interpolation(SubConfig):
#     wdic: bool # False
#
#
# class Withdrawal segment(SubConfig):
#     iwd: int
#
#
# class Withdrawal elevation(SubConfig):
#     ewd: float
#
#
# class Withdrawal top layer(SubConfig):
#     ktwd: int
#
#
# class Withdrawal bottom layer(SubConfig):
#     kbwd: int
#
#
# class Tributary inflow placement(SubConfig):
#     trc: InflowEntryType
#
#
# class Tributary interpolation(SubConfig):
#     tric: bool # True
#
#
# class Tributary segment(SubConfig):
#     itr: int
#
#
# class Tributary inflow top elevation(SubConfig):
#     etrt: float
#
#
# class Tributary inflow bottom elevation(SubConfig):
#     etrb: float
#
#
# class Distributed tributaries(SubConfig):
#     dtrc: bool # False
#
#
# class Hydrodynamic output control(SubConfig):
#     hprwbc: bool # False
#
#
# class Snapshot print(SubConfig):
#     snpc: bool # False
#     nsnp: int
#     nisnp: int
#
#
# class Snapshot dates(SubConfig):
#     snpd: float
#
#
# class Snapshot frequency(SubConfig):
#     snpf: float
#
#
# class Snapshot segments(SubConfig):
#     isnp: int
#
#
# class Screen print(SubConfig):
#     scrc: bool # False
#     nscr: int
#
#
# class Screen dates(SubConfig):
#     scrd: float
#
#
# class Screen frequency(SubConfig):
#     scrf: float
#
#
# class Profile plot(SubConfig):
#     prfc: bool # False
#     nprf: int
#     niprf: int
#
#
# class Profile date(SubConfig):
#     prfd: float
#
#
# class Profile frequency(SubConfig):
#     prff: float
#
#
# class Profile segment(SubConfig):
#     iprf: int
