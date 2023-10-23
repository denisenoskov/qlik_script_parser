__doc__ = """
This module contains various classes that can be used to match
all sorts of QLIK script patterns.

Classes & methods
-------------------------------------------

Below are listed all classes within :py:mod:`pregex.meta.qlik_script`
along with any possible methods they may possess.
"""

__all__ = ['find_match']

import re
from typing import Union, Tuple

import pregex.core.classes as _cl
import pregex.core.groups as _gr
import pregex.core.operators as _op
import pregex.core.pre as _pre
from .types import VarData, VarTypes, Vars


class _SingletonMeta(type):
    """Контроллер синглтонов, чтобы не создавались лишние объекты.
    Не учитывает возможные параметры при создании объекта из них
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class _VarName(_pre.Pregex, metaclass=_SingletonMeta):
    """Имя переменной в скрипте"""

    def __init__(self):
        pre = _cl.AnyLetter() + _op.Either(_cl.AnyDigit(), _cl.AnyWordChar(), _pre.Pregex('.'),
                                           _pre.Pregex('_')).at_least(0)
        super().__init__(str(pre), escape=False)


class _WhitespaceOptional(_pre.Pregex, metaclass=_SingletonMeta):
    def __init__(self):
        super().__init__(str(_cl.AnyWhitespace().at_least(0)), escape=False)


class _Equal(_pre.Pregex, metaclass=_SingletonMeta):
    def __init__(self):
        super().__init__('=', escape=False)


class _Value(_pre.Pregex, metaclass=_SingletonMeta):
    def __init__(self):
        super().__init__(str(_cl.Any().at_least(0)), escape=False)


class SetVar(_pre.Pregex, metaclass=_SingletonMeta):
    """
    Команда SET или LET
    """

    def __init__(self):
        command = _op.Either('SET', 'LET')
        var_name = _VarName()
        whitespace_optional = _WhitespaceOptional()
        equal = _Equal()
        value = _Value()
        pre = whitespace_optional + command + whitespace_optional + _gr.Capture(var_name) + \
              whitespace_optional + equal + whitespace_optional + _gr.Capture(value)

        super().__init__(str(pre), escape=False)

    def get_data(self, text, vars_: Vars) -> Tuple[Union[str, None], Union[VarData, None]]:
        """

        Args:
            vars_:
            text:

        Returns:

        """
        data = re.findall(self.get_pattern(), text)
        if not data:
            return None, None
        elif len(data) > 1:
            return None, None
        else:
            value = data[0][1].strip()
            if value.isdecimal():
                value = float(data[0][1])
            elif value.isdigit():
                value = int(data[0][1])
            elif re.search(r'^[\'"]([^\'"]*)[\':]$', value):
                value = value[1:-1]
            return data[0][0], VarData(typ=VarTypes.VARIABLE, value=value)

    def proceed(self, text, vars_: Vars, current_line_number: int):
        """

        Args:
            current_line_number:
            text:
            vars_:

        Returns:

        """
        name, data = self.get_data(text, vars_)
        if name and data['typ']:
            vars_[name] = data
            current_line_number += 1
            return True
        else:
            return False


regex = [SetVar()]


def _calc_extension(value, vars_: Vars):
    for v in vars_:
        value = value.replace(f'$({v})', vars_[v]['value'])
    return value


def _calc_expression(value, vars_: Vars):
    """Рассчитывает конкретную строку -
    подставляет значение переменных, выполняет известные функции
    В результате выполнения, сохраняет
    """

    value = _calc_extension(value, vars_)

    return value


def find_match(line: str, vars_: Vars, current_line_number: int):
    """Ищет совпадение среди шаблонов, если находит - производит манипуляции
    Returns:
        True - если нашел, False - если не нашел шаблон
    """
    line = _calc_expression(line, vars_)
    for reg in regex:
        if reg.proceed(line, vars_, current_line_number):
            return True
    return False
