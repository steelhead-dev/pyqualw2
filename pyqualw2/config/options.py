from enum import Enum, auto


class WTYPEC(Enum):
    FRESH = auto()
    SALT = auto()


class GRIDC(Enum):
    RECT = auto()
    TRAP = auto()


class SLHTC(Enum):
    TERM = auto()
    ET = auto()


class ICEC(Enum):
    ON = auto()
    ONWB = auto()
    OFF = auto()


class SLICEC(Enum):
    SIMPLE = auto()
    DETAIL = auto()


class SLTRC(Enum):
    ULTIMATE = auto()
    QUICKEST = auto()
    UPWIND = auto()


class FRICC(Enum):
    MANN = auto()
    CHEZY = auto()


class AZC(Enum):
    NICK = auto()
    PARAB = auto()
    RNG = auto()
    W2 = auto()
    W2N = auto()
    TKE = auto()
    TKE1 = auto()


class ImplicitExplicit(Enum):
    IMP = auto()
    EXP = auto()


class SINKC(Enum):
    POINT = auto()
    LINE = auto()


class WithdrawalType(Enum):
    DOWN = auto()
    LAT = auto()


class InflowEntryType(Enum):
    DISTR = auto()
    DENSITY = auto()
    SPECIFY = auto()


class DYNGTC(Enum):
    B = auto()
    ZGT = auto()
    FLOW = auto()
