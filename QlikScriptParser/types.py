from __future__ import annotations

from enum import Enum
from typing import TypedDict, Union, Dict, List


class VarTypes(Enum):
    VARIABLE = 1
    SUB = 2


class VarData(TypedDict):
    typ: VarTypes
    value: Union[str, int, float]


Vars = Dict[str, VarData]


class ScriptData:
    script: Dict[int, str]
    vars: Vars
    current_interpretater_line: int

    def __init__(self):
        self.script = {}
        self.vars = {}
        self.current_interpretater_line = 0
