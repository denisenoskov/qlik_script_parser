__doc__ = """
https://help.qlik.com/ru-RU/cloud-services/Subsystems/Hub/Content/Sense_Hub/Scripting/script-statements-keywords.htm
"""

__all__ = ['find_match']

import re
from typing import Union, Tuple

import pregex.core.classes as _cl
import pregex.core.groups as _gr
import pregex.core.operators as _op
import pregex.core.pre as _pre
from .types import VarData, VarTypes, ScriptData

import abc

import logging


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


class _ScriptElement(_pre.Pregex, metaclass=_SingletonMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RegexTemp(_pre.Pregex, metaclass=_SingletonMeta):
    """Шаблон для разработки классов регулярных выражений команд скрипта"""

    def __init__(self, *args, **kwargs):
        super(RegexTemp, self).__init__(*args, **kwargs)
        pass

    @abc.abstractmethod
    def proceed(self, line: str, script_data: ScriptData):
        """Выполнить ценностное действие, перевести указатель на следующую строку скрипта
        Args:
            line: текущая строка для обработки
            script_data: данные интерпретатора в момент выполнения
        Returns:
            Флаг того что шаблон подходит и действия выполнены успешно
            """


class _VarName(_ScriptElement):
    """Имя переменной в скрипте"""

    def __init__(self):
        pre = _cl.AnyLetter() + _op.Either(_cl.AnyDigit(), _cl.AnyWordChar(), _pre.Pregex('.'),
                                           _pre.Pregex('_')).at_least(0)
        super().__init__(str(pre), escape=False)


class _WhitespaceOptional(_ScriptElement):
    """Опциональные пробелы"""
    def __init__(self):
        super().__init__(str(_cl.AnyWhitespace().at_least(0)), escape=False)


class _WhitespaceRequired(_ScriptElement):
    """Обязательные пробелы пробелы"""
    def __init__(self):
        super().__init__(str(_cl.AnyWhitespace().at_least(1)), escape=False)


class _Equal(_ScriptElement):
    """Знак равенства"""
    def __init__(self):
        super().__init__('=', escape=False)


class _Value(_ScriptElement):
    """Значение которое присвоится переменной"""
    def __init__(self):
        super().__init__(str(_cl.Any().at_least(0)), escape=False)


class SetVar(RegexTemp):
    """
    Команда SET или LET
    """
    def __init__(self):
        command = _op.Either('SET', 'LET')
        var_name = _VarName()
        whitespace_required = _WhitespaceRequired()
        whitespace_optional = _WhitespaceOptional()
        equal = _Equal()
        value = _Value()
        pre = whitespace_optional + command + whitespace_required + _gr.Capture(var_name) + \
            whitespace_required + equal + whitespace_required + _gr.Capture(value)

        super().__init__(str(pre), escape=False)

    def _get_data(self, line) -> Tuple[Union[str, None], Union[VarData, None]]:
        """Получить значение которое присвоится переменной
        Args:
            line: строка
        Returns:
            Если шаблон не совпал, или совпал несколько раз - возвращает (None, None)
            Иначе, возвращает имя переменной и ее значение
        """
        data = re.findall(self.get_pattern(), line, flags=re.I)
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

    def proceed(self, line, script_data: ScriptData):
        """Выполнить присвоение переменой значения

        Args:
            line: текущая команда
            script_data: данные интерпретатора в текущий момент
        Returns:
            Флаг того что это команда подошла и присвоение переменой прошло успешно
        """
        name, data = self._get_data(line)
        logging.debug(f'нашли данные - {name, data}')

        if name and data['typ']:
            script_data.vars[name] = data
            script_data.current_interpretater_line += 1
            return True
        else:
            return False


regex = [SetVar()]


def find_match(line: str, script_data: ScriptData):
    """Ищет совпадение среди шаблонов, если находит - вызывает функцию proceed. Она выполняет заложенное действие.
    А также, изменение следующей строки
    Returns:
        Флаг успешности поиска и выполнения команды
    """
    for reg in regex:
        logging.debug(f'ищем строку - {line}')
        if reg.proceed(line, script_data):
            return True
    script_data.current_interpretater_line += 1
    return False

