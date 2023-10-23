import logging
import re

from .qlik_script_regex import find_match
from .types import Vars


class QlikScriptParser:
    """

    """
    _vars: Vars
    _sources = {}
    _connections = {}
    _line_re = r'([^;]*);'
    _script_lines = []

    def __init__(self, script_text: str):
        self._script_text = script_text
        self._parse()

    def _parse(self):
        script_text = self._clean_script()
        lines = re.findall(self._line_re, script_text, flags=re.IGNORECASE | re.DOTALL)
        current_line_number = 0
        while True:
            line = lines[current_line_number]

            if not find_match(line, self._vars, current_line_number):
                logging.warning(f'Строка не определена - {line}')

    def _clean_script(self) -> str:
        """Удаляем комментарии, строки переноса
        Returns: текст скрипта без комментариев и переносов"""
        script_text = self._script_text
        script_text = re.sub(r'[^:\w](//.*)', '', script_text, count=0)
        script_text = re.sub(r'^\s*REM .*', '', script_text, count=0, flags=re.I)
        script_text = re.sub(r'/\*.*?\*/', '', script_text, count=0, flags=re.S | re.I)
        script_text = script_text.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
        return script_text
