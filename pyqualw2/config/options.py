from enum import Enum


class WTYPEC(Enum):
    FRESH = "FRESH"
    SALT = "SALT"


class GRIDC(Enum):
    RECT = "RECT"
    TRAP = "TRAP"


class SLHTC(Enum):
    TERM = "TERM"
    ET = "ET"


class ICEC(Enum):
    ON = "ON"
    ONWB = "ONWB"
    OFF = "OFF"


class SLICEC(Enum):
    SIMPLE = "SIMPLE"
    DETAIL = "DETAIL"


class SLTRC(Enum):
    ULTIMATE = "ULTIMATE"
    QUICKEST = "QUICKEST"
    UPWIND = "UPWIND"


class FRICC(Enum):
    MANN = "MANN"
    CHEZY = "CHEZY"


class AZC(Enum):
    NICK = "NICK"
    PARAB = "PARAB"
    RNG = "RNG"
    W2 = "W2"
    W2N = "W2N"
    TKE = "TKE"
    TKE1 = "TKE1"


class ImplicitExplicit(Enum):
    IMP = "IMP"
    EXP = "EXP"


class SINKC(Enum):
    POINT = "POINT"
    LINE = "LINE"


class WithdrawalType(Enum):
    DOWN = "DOWN"
    LAT = "LAT"


class InflowEntryType(Enum):
    DISTR = "DISTR"
    DENSITY = "DENSITY"
    SPECIFY = "SPECIFY"


class DYNGTC(Enum):
    B = "B"
    ZGT = "ZGT"
    FLOW = "FLOW"
