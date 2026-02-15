# aeditor.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from anumber import DECIMAL_SEPARATOR, ZERO_STRING


# Команды редактора (по примеру констант C++) [file:1]
C_ZERO = 0
C_ONE = 1
C_TWO = 2
C_THREE = 3
C_FOUR = 4
C_FIVE = 5
C_SIX = 6
C_SEVEN = 7
C_EIGHT = 8
C_NINE = 9
C_SIGN = 10
C_SEPARATOR_FR = 11
C_SEPARATOR_C = 12
C_BS = 13
C_CE = 14


class AEditor(ABC):
    """
    Абстрактный редактор чисел (AEditor). [file:1]
    Отвечает за ввод, хранение и редактирование строкового представления числа.
    """

    def __init__(self, initial: str = ZERO_STRING, separator: str = DECIMAL_SEPARATOR) -> None:
        self._string = initial
        self._separator = separator
        self._separator_is = DECIMAL_SEPARATOR in initial

    # Свойство «строка» [file:1]

    @property
    def string(self) -> str:
        """читатьСтрокаВформатеСтроки: String; [file:1]"""
        return self._string

    @string.setter
    def string(self, value: str) -> None:
        """писатьСтрокаВформатеСтроки(a: String); [file:1]"""
        self._string = value
        self._separator_is = self._separator in self._string

    @property
    def separator_is(self) -> bool:
        return self._separator_is

    # Абстрактные операции нижнего уровня

    @abstractmethod
    def _add_digit_ls(self, digit: int) -> None:
        """Добавить цифру слева от разделителя. [file:1]"""

    @abstractmethod
    def _add_digit_rs(self, digit: int) -> None:
        """Добавить цифру справа от разделителя. [file:1]"""

    # Общие операции

    @abstractmethod
    def is_zero(self) -> bool:
        """число есть ноль [file:1]"""

    @abstractmethod
    def add_separator(self) -> str:
        """добавить разделитель [file:1]"""

    @abstractmethod
    def add_digit(self, digit: int) -> str:
        """добавить цифру [file:1]"""

    @abstractmethod
    def add_sign(self) -> str:
        """добавить/изменить знак [file:1]"""

    @abstractmethod
    def backspace(self) -> str:
        """забой символа [file:1]"""

    @abstractmethod
    def clear(self) -> str:
        """очистить: установить ноль [file:1]"""

    def edit(self, command: int) -> str:
        """
        редактировать(a: Integer): String – диспетчер команд редактора. [file:1]
        """
        if command in (C_ZERO, C_ONE, C_TWO, C_THREE, C_FOUR,
                       C_FIVE, C_SIX, C_SEVEN, C_EIGHT, C_NINE):
            digit = command
            return self.add_digit(digit)
        elif command == C_SIGN:
            return self.add_sign()
        elif command in (C_SEPARATOR_FR, C_SEPARATOR_C):
            return self.add_separator()
        elif command == C_BS:
            return self.backspace()
        elif command == C_CE:
            return self.clear()
        else:
            return self.string


class FEditor(AEditor):
    """
    Редактор простых дробей (FEditor). [file:1]
    Формат: знаковая строка с символом '/' как разделителем числителя и знаменателя.
    """

    FRACTION_SEPARATOR = "/"

    def __init__(self) -> None:
        super().__init__(ZERO_STRING, DECIMAL_SEPARATOR)
        self._zero = ZERO_STRING
        self._sign = "-"  # изображение знака [file:1]

    def _add_digit_ls(self, digit: int) -> None:
        if self.is_zero():
            self._string = str(digit)
        else:
            self._string += str(digit)

    def _add_digit_rs(self, digit: int) -> None:
        # Для простых дробей можно трактовать всё как одну строку до "/". [file:1]
        self._add_digit_ls(digit)

    def is_zero(self) -> bool:
        return self._string in ("", self._zero, self._sign + self._zero)

    def add_separator(self) -> str:
        if self.FRACTION_SEPARATOR not in self._string:
            if self.is_zero():
                self._string = self._zero + self.FRACTION_SEPARATOR
            else:
                self._string += self.FRACTION_SEPARATOR
        return self._string

    def add_digit(self, digit: int) -> str:
        if not (0 <= digit <= 9):
            return self._string
        if self.is_zero():
            self._string = str(digit)
        else:
            self._string += str(digit)
        return self._string

    def add_sign(self) -> str:
        if self._string == "0" or self._string == "-0":
            self._string = "-0"
            return self._string

        if self._string.startswith("-"):
            if self._string == "-0":
                self._string = "0"
            else:
                self._string = self._string[1:]  # Убираем минус
        else:
            self._string = "-" + self._string  # Добавляем минус

        return self._string

    def backspace(self) -> str:
        if len(self._string) <= 1:
            self._string = self._zero
        else:
            self._string = self._string[:-1]
        return self._string

    def clear(self) -> str:
        self._string = "0"
        return self._string


class PEditor(FEditor):
    """
    Редактор p-ичных/вещественных чисел (PEditor). Наследует FEditor. [file:1]
    Использует DECIMAL_SEPARATOR как разделитель целой и дробной частей.
    """

    def __init__(self) -> None:
        super().__init__()
        self._separator = DECIMAL_SEPARATOR
        self._separator_is = False

    def _add_digit_rs(self, digit: int) -> None:
        # Для вещественных чисел учитываем наличие разделителя. [file:1]
        if self._separator in self._string:
            self._string += str(digit)
        else:
            self._add_digit_ls(digit)

    def add_separator(self) -> str:
        if self._separator not in self._string:
            if self.is_zero():
                self._string = ZERO_STRING + self._separator
            else:
                self._string += self._separator
            self._separator_is = True
        return self._string


class CEditor(AEditor):
    """
    Редактор комплексных чисел (CEditor). [file:1]
    Использует два PEditor для действительной и мнимой частей.
    """

    COMPLEX_SEPARATOR = " i* "

    def __init__(self) -> None:
        super().__init__(ZERO_STRING, DECIMAL_SEPARATOR)
        self._zero = ZERO_STRING
        self._re_editor = PEditor()
        self._im_editor = PEditor()
        self._edit_imag = False  # редактируемая часть: False – Re, True – Im

    def _sync_string(self) -> None:
        self._string = f"{self._re_editor.string}{self.COMPLEX_SEPARATOR}{self._im_editor.string}"

    def _add_digit_ls(self, digit: int) -> None:
        if self._edit_imag:
            self._im_editor._add_digit_ls(digit)
        else:
            self._re_editor._add_digit_ls(digit)
        self._sync_string()

    def _add_digit_rs(self, digit: int) -> None:
        if self._edit_imag:
            self._im_editor._add_digit_rs(digit)
        else:
            self._re_editor._add_digit_rs(digit)
        self._sync_string()

    def is_zero(self) -> bool:
        return self._re_editor.is_zero() and self._im_editor.is_zero()

    def add_separator(self) -> str:
        # Разделитель между частями комплексного числа [file:1]
        self._edit_imag = True
        self._sync_string()
        return self._string

    def add_digit(self, digit: int) -> str:
        if not (0 <= digit <= 9):
            return self._string
        self._add_digit_ls(digit)
        return self._string

    def add_sign(self) -> str:
        """Минус для комплексного."""
        if self._edit_imag:  # Im часть
            self._im_editor.add_sign()
        else:  # Re часть
            self._re_editor.add_sign()
        self._sync_string()
        return self._string

    def backspace(self) -> str:
        if self._edit_imag:
            self._im_editor.backspace()
        else:
            self._re_editor.backspace()
        self._sync_string()
        return self._string

    def clear(self) -> str:
        self._re_editor.clear()
        self._im_editor.clear()
        self._edit_imag = False
        self._sync_string()
        return self._string
