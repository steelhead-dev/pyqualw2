from typing import Self
import warnings
from typing import Any

from pydantic import BaseModel, ConfigDict

type ParseResult = tuple[Self, list[str]]


class SubConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

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
        fields = set(cls.model_fields.keys())
        args = set(values.keys())
        extra = args - fields
        if extra:
            warnings.warn(f"Extra fields passed to {cls.__name__}: {extra}")
        return values

    def parse(cls, lines: list[str]) -> ParseResult:
        pass


class Title(SubConfig):
    title: str

    @classmethod
    def parse(cls, lines: list[str]) -> ParseResult:
        return cls(title="\n".join(lines[1:11])), lines[12:]


class GridDimensions(SubConfig):
    nwb: int
    nbr: int
    imx: int
    kmx: int
    nproc: int
    closec: bool

    @classmethod
    def parse(cls, lines: list[str]) -> ParseResult:
        kwargs = {}
        for key, value in zip(lines[0].split(","), lines[1].split(","), strict=True):
            kwargs[key] = value
        return cls(**kwargs), lines[2:]


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
    def parse(cls, lines: list[str]) -> ParseResult:
        kwargs = {}
        for key, value in zip(lines[0].split(","), lines[1].split(","), strict=True):
            kwargs[key] = value
        return cls(**kwargs), lines[2:]


class Constituents(SubConfig):
    ngc: int
    nss: int
    nal: int
    nep: int
    nbod: int
    nmc: int
    nzp: int

    @classmethod
    def parse(cls, lines: list[str]) -> ParseResult:
        kwargs = {}
        for key, value in zip(lines[0].split(","), lines[1].split(","), strict=True):
            kwargs[key] = value
        return cls(**kwargs), lines[2:]


class Miscellaneous(SubConfig):
    nday: int
    selectc: str
    habitatc: bool
    envirpc: bool
    aeratec: bool
    inituwl: bool
    orcc: bool
    sed_diag: bool

    @classmethod
    def parse(cls, lines: list[str]) -> ParseResult:
        kwargs = {}
        for key, value in zip(lines[0].split(","), lines[1].split(","), strict=True):
            kwargs[key] = value
        return cls(**kwargs), lines[2:]


class TimeControl(SubConfig):
    tmstrt: float
    tmend: float
    year: int

    @classmethod
    def parse(cls, lines: list[str]) -> ParseResult:
        kwargs = {}
        for key, value in zip(lines[0].split(","), lines[1].split(","), strict=True):
            kwargs[key] = value
        return cls(**kwargs), lines[2:]


class TimestepControl(SubConfig):
    ndt: int
    dltmin: float
    dltintr: bool

    @classmethod
    def parse(cls, lines: list[str]) -> ParseResult:
        kwargs = {}
        for key, value in zip(lines[0].split(","), lines[1].split(","), strict=True):
            kwargs[key] = value
        return cls(**kwargs), lines[2:]


class TimestepDate(SubConfig):
    dltd: list[float]

    @classmethod
    def parse(cls, lines: list[str]) -> ParseResult:
        res = [val for val in lines[1].split(",") if val != ""]
        return cls(dltd=res), lines[2:]


class MaximumTimestep(SubConfig):
    dltmax: list[float]

    @classmethod
    def parse(cls, lines: list[str]) -> ParseResult:
        res = [val for val in lines[1].split(",") if val != ""]
        return cls(dltmax=res), lines[2:]


class TimestepFraction(SubConfig):
    dltf: list[float]

    @classmethod
    def parse(cls, lines: list[str]) -> ParseResult:
        res = [val for val in lines[1].split(",") if val != ""]
        return cls(dltf=res), lines[2:]


class TimestepLimitations(SubConfig):
    visc: bool
    celc: bool
    dltadd: bool

    @classmethod
    def parse(cls, lines: list[str]) -> ParseResult:
        return cls(
            visc=lines[1].split(",")[0],
            celc=lines[2].split(",")[0],
            dltadd=lines[3].split(",")[0],
        )


# # TODO
#
# class Branch geometry(SubConfig):
#     us: int
#     ds: int
#     uhs: int
#     dhs: int
#     nlmin: int
#     slope: float
#     slopec: float
#
#
# class Waterbody definition(SubConfig):
#     lat: float
#     long: float
#     ebot: float
#     bs: int
#     be: int
#     jbdn: int
#
#
# class Initial conditions(SubConfig):
#     t2i: float
#     icethi: float
#     wtypec: WTYPEC
#     gridc: GRIDC
#
#
# class Calculations(SubConfig):
#     vbc: bool = True
#     ebc: bool = True
#     mbc: bool = True
#     pqc: bool = False
#     evc: bool = True
#     prc: bool = False
#
#
# class Dead sea(SubConfig):
#     windc: bool = True
#     qinc: bool = True
#     qoutc: bool = True
#     heatc: bool = True
#
#
# class Interpolation(SubConfig):
#     qinic: bool = True
#     dtric: bool = True
#     hdic: bool = True
#
#
# class Heat exchange(SubConfig):
#     slhtc: SLHTC = SLHTC.TERM
#     sroc: bool = False
#     rhevap: bool = False
#     metic: bool = True
#     fetchc: bool = False
#     afw: float = 9.2
#     bfw: float = 0.46
#     cfw: float = 2.0
#     windh: float
#
#
# class Ice cover(SubConfig):
#     icec: ICEC = ICEC.OFF
#     slicec: SLICEC = SLICEC.DETAIL
#     albedo: float = 0.25
#     hwi: float = 10.0
#     betai: float = 0.6
#     gammai: float = 0.07
#     icemin: float = 0.05
#     icet2: float = 3.0
#
#
# class Transport scheme(SubConfig):
#     sltrc: SLTRC = SLTRC.ULTIMATE
#     theta: float = 0.55
#
#
# class Hydraulic coefficients(SubConfig):
#     ax: float = 1.0
#     dx: float = 1.0
#     cbhe: float = 0.3
#     tsed: float
#     fi: float = 0.01
#     tsedf: float = 1.0
#     fricc: FRICC = FRICC.CHEZY
#     z0: float = 0.001
#
#
# class Vertical Eddy Viscosity(SubConfig):
#     azc: AZC = AZC.TKE
#     azslc: AZSLC = AZSLC.IMP
#     azmax: float = 1.0
#     fbc: int = 3
#     e: float = 9.535
#     arodi: float = 0.431
#     strcklr: float = 24.0
#     boundfr: float = 10.0
#     tkecal: TKECAL = TKECAL.IMP
#
#
# class Number of structures(SubConfig):
#     nstr: int
#     dynstruc: bool
#
#
# class Structure interpolation(SubConfig):
#     stric: bool = False
#
#
# class Structure top selective withdrawal limit(SubConfig):
#     ktstr: int
#
#
# class Structure bottom selective withdrawal liimit(SubConfig):
#     kbstr: int
#
#
# class Sink type(SubConfig):
#     sinkc: SINKC = SINKC.POINT
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
#     pupic: InflowEntryType = InflowEntryType.DISTR
#     etupi: float
#     ebupi: float
#     ktupi: int
#     kbupi: int
#
#
# class Downstream pipe(SubConfig):
#     pdpic: InflowEntryType = InflowEntryType.DISTR
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
#     puspc: InflowEntryType = InflowEntryType.DISTR
#     etusp: float
#     ebusp: float
#     ktusp: int
#     kbusp: int
#
#
# class Downstream spillways(SubConfig):
#     pdspc: InflowEntryType = InflowEntryType.DISTR
#     etdsp: float
#     ebdsp: float
#     ktdsp: int
#     kbdsp: int
#
#
# class Spillway dissolved gas(SubConfig):
#     gasspc: bool = False
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
#     pugtc: InflowEntryType = InflowEntryType.DISTR
#     etugt: float
#     ebugt: float
#     ktugt: int
#     kbugt: int
#
#
# class Downstream gate(SubConfig):
#     pdgtc: InflowEntryType = InflowEntryType.DISTR
#     etdgt: float
#     ebdgt: float
#     ktdgt: int
#     kbdgt: int
#
#
# class Gate dissolved gas(SubConfig):
#     gasgtc: bool = False
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
#     latpuc: WithdrawalType = WithdrawalType.DOWN
#     dynpump: bool = False
#
#
# class Pumps 2(SubConfig):
#     ppuc: InflowEntryType = InflowEntryType.DISTR
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
#     wdic: bool = False
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
#     tric: bool = True
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
#     dtrc: bool = False
#
#
# class Hydrodynamic output control(SubConfig):
#     hprwbc: bool = False
#
#
# class Snapshot print(SubConfig):
#     snpc: bool = False
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
#     scrc: bool = False
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
#     prfc: bool = False
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
