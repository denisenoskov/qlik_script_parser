from __future__ import annotations

from enum import Enum
from typing import TypedDict, Union, Dict


class VarTypes(Enum):
    VARIABLE = 1
    SUB = 2


class VarData(TypedDict):
    typ: VarTypes
    value: Union[str, int, float]


Vars = Dict[str, VarData]
