import logging
import re

from .qlik_script_regex import find_match
from .types import ScriptData


class QlikScriptParser:
    """

    """
    _line_re = r'([^;]*);'
    _script_lines = []
    _script_data = ScriptData()

    def __init__(self, script_text: str):
        self._script_text = script_text
        self._parse()
        logging.warning(self._script_data.vars)

    def _parse(self):
        """Парсинг скрипта"""
        script_text = self._clean_script()

        lines = re.findall(self._line_re, script_text, flags=re.IGNORECASE | re.DOTALL)

        self._script_data.current_interpretater_line = 0
        while True:
            try:
                line = lines[self._script_data.current_interpretater_line]
            except IndexError:
                break
            line = self._calc_expression(line)
            is_regex_found = find_match(line, self._script_data)
            if not is_regex_found:
                logging.warning(f'Строка не определена - {line}')

    def _clean_script(self) -> str:
        """Удаляем комментарии, строки переноса
        Returns: текст скрипта без комментариев и переносов"""
        script_text = self._script_text
        script_text = re.sub(r'[^:\w](//.*)', '', script_text, count=0)
        script_text = re.sub(r'^\s*REM .*', '', script_text, count=0, flags=re.I)
        script_text = re.sub(r'/\*.*?\*/', '', script_text, count=0, flags=re.S | re.I)
        script_text = script_text.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
        # Добавляю ";" в конец этих строк для разделения управляющих конструкций,
        # по нотации QLIK не устанавливается в конце разделитель ";"
        script_text = re.sub(r'(^\s*(FOR|NEXT|SUB|CASE|SWITCH|IF|THEN|DO|LOOP|CALL)\s+[^;]*)', '\1 ;', script_text,
                             flags=re.IGNORECASE)
        return script_text

    def _calc_expansions(self, line):
        """Расчет расширений, подмена переменных на их значение
        https://help.qlik.com/ru-RU/cloud-services/Subsystems/Hub/Content/Sense_Hub/Scripting/dollar-sign-expansions.htm"""
        for var, value in self._script_data.vars.items():
            line = line.replace(f'$({var})', value['value'])
        return line

    def _calc_funcs(self, line):
        """Выполнить функции в выражении
        https://help.qlik.com/ru-RU/cloud-services/Subsystems/Hub/Content/Sense_Hub/Scripting/functions-in-scripts-chart-expressions.htm"""
        return line

    def _calc_operation(self, line):
        """Выполнить операции в выражении, такие как сложение строк, или математические операции
        https://help.qlik.com/ru-RU/cloud-services/Subsystems/Hub/Content/Sense_Hub/Scripting/Operators/operators.htm"""
        return line

    def _calc_expression(self, line):
        """Рассчитывает конкретную строку -
        подставляет значение переменных, выполняет известные функции
        В результате выполнения, получаем строку
        """
        line = self._calc_expansions(line)
        line = self._calc_funcs(line)
        line = self._calc_operation(line)
        return line
