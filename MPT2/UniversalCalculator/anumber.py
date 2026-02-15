# anumber.py
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar
import math

# Константы (разделитель и строка нуля) [file:1]
DECIMAL_SEPARATOR = "."
ZERO_STRING = "0"

TNumber = TypeVar("TNumber", bound="TANumber")


class TANumber(ABC):
    """
    Абстрактный класс Число (TANumber).
    Обеспечивает арифметические операции над p-ичными числами,
    простыми дробями и комплексными числами. [file:1]
    """

    def __init__(self, value: str = ZERO_STRING) -> None:
        self._string = value  # строковое представление числа [file:1]

    # --- Абстрактные арифметические операции ---

    @abstractmethod
    def is_zero(self) -> bool:
        """числоЕстьНоль(B: TANumber): Boolean; [file:1]"""

    @abstractmethod
    def copy(self: TNumber) -> TNumber:
        """копировать: TANumber; [file:1]"""

    @abstractmethod
    def add(self: TNumber, other: TANumber) -> TNumber:
        """сложить (B: TANumber): TANumber; [file:1]"""

    @abstractmethod
    def sub(self: TNumber, other: TANumber) -> TNumber:
        """вычесть (B: TANumber): TANumber; [file:1]"""

    @abstractmethod
    def mul(self: TNumber, other: TANumber) -> TNumber:
        """перемножить (B: TANumber): TANumber; [file:1]"""

    @abstractmethod
    def div(self: TNumber, other: TANumber) -> TNumber:
        """поделить (B: TANumber): TANumber; [file:1]"""

    @abstractmethod
    def equals(self, other: TANumber) -> bool:
        """равенствоЧисел (B: TANumber): Boolean; [file:1]"""

    @abstractmethod
    def sqr(self: TNumber) -> TNumber:
        """квадрат: TANumber; [file:1]"""

    @abstractmethod
    def inv(self: TNumber) -> TNumber:
        """обратное: TANumber; [file:1]"""

    # --- Свойство String (строковое представление числа) ---

    @property
    def string(self) -> str:
        """читатьЧислоВформатеСтроки: String; [file:1]"""
        return self._string

    @string.setter
    def string(self, value: str) -> None:
        """писатьЧислоВформатеСтроки(a: String); [file:1]"""
        self._string = value

    # Удобство для отладки
    def __str__(self) -> str:
        return self.string

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.string!r})"


@dataclass
class TPNumber(TANumber):
    """
    TPNumber – p-ичное число с основанием 2..16. [file:1]
    Формат строки: целая и дробная части в системе base через DECIMAL_SEPARATOR.
    """

    base: int = 10

    def __init__(self, value: str = ZERO_STRING, base: int = 10) -> None:
        super().__init__(value)
        if not (2 <= base <= 16):
            raise ValueError("Основание системы счисления должно быть в диапазоне 2..16")
        self.base = base

    # Внутренние вспомогательные методы

    def _to_float(self) -> float:
        # Используем стандартное преобразование для упрощения. [file:1]
        return float(self.string.replace(DECIMAL_SEPARATOR, "."))

    def _from_float(self, x: float) -> str:
        s = f"{x}".replace(".", DECIMAL_SEPARATOR)
        return s

    # Реализация абстрактных методов

    def is_zero(self) -> bool:
        try:
            return self._to_float() == 0.0
        except ValueError:
            return False

    def copy(self) -> "TPNumber":
        return TPNumber(self.string, self.base)

    def add(self, other: TANumber) -> "TPNumber":
        v = self._to_float() + TPNumber(str(other), self.base)._to_float()
        return TPNumber(self._from_float(v), self.base)

    def sub(self, other: TANumber) -> "TPNumber":
        v = self._to_float() - TPNumber(str(other), self.base)._to_float()
        return TPNumber(self._from_float(v), self.base)

    def mul(self, other: TANumber) -> "TPNumber":
        v = self._to_float() * TPNumber(str(other), self.base)._to_float()
        return TPNumber(self._from_float(v), self.base)

    def div(self, other: TANumber) -> "TPNumber":
        other_val = TPNumber(str(other), self.base)._to_float()
        if other_val == 0.0:
            raise ZeroDivisionError("Деление на ноль")
        v = self._to_float() / other_val
        return TPNumber(self._from_float(v), self.base)

    def equals(self, other: TANumber) -> bool:
        return self._to_float() == TPNumber(str(other), self.base)._to_float()

    def sqr(self) -> "TPNumber":
        v = self._to_float() ** 2
        return TPNumber(self._from_float(v), self.base)

    def inv(self) -> "TPNumber":
        if self.is_zero():
            raise ZeroDivisionError("Обратное к нулю не существует")
        v = 1.0 / self._to_float()
        return TPNumber(self._from_float(v), self.base)


@dataclass
class TFrac(TANumber):
    """
    TFrac – простая дробь n/d. [file:1]
    Формат строки: "n/d".
    """

    numerator: int = 0
    denominator: int = 1

    def __init__(self, value: str = ZERO_STRING) -> None:
        super().__init__(value)
        self._parse_from_string(value)

    # Внутренние методы

    def _parse_from_string(self, s: str) -> None:
        if "/" in s:
            num_s, den_s = s.split("/", 1)
            self.numerator = int(num_s)
            self.denominator = int(den_s)
        else:
            self.numerator = int(s)
            self.denominator = 1
        if self.denominator == 0:
            raise ZeroDivisionError("Знаменатель не может быть равен 0")
        self._normalize()

    def _normalize(self) -> None:
        if self.denominator < 0:
            self.denominator *= -1
            self.numerator *= -1
        g = math.gcd(self.numerator, self.denominator)
        if g != 0:
            self.numerator //= g
            self.denominator //= g
        self._update_string()

    def _update_string(self) -> None:
        if self.denominator == 1:
            self.string = str(self.numerator)
        else:
            self.string = f"{self.numerator}/{self.denominator}"

    # Реализация абстрактных методов

    def is_zero(self) -> bool:
        return self.numerator == 0

    def copy(self) -> "TFrac":
        return TFrac(self.string)

    def add(self, other: TANumber) -> "TFrac":
        o = TFrac(str(other))
        n = self.numerator * o.denominator + self.denominator * o.numerator
        d = self.denominator * o.denominator
        return TFrac(f"{n}/{d}")

    def sub(self, other: TANumber) -> "TFrac":
        o = TFrac(str(other))
        n = self.numerator * o.denominator - self.denominator * o.numerator
        d = self.denominator * o.denominator
        return TFrac(f"{n}/{d}")

    def mul(self, other: TANumber) -> "TFrac":
        o = TFrac(str(other))
        n = self.numerator * o.numerator
        d = self.denominator * o.denominator
        return TFrac(f"{n}/{d}")

    def div(self, other: TANumber) -> "TFrac":
        o = TFrac(str(other))
        if o.numerator == 0:
            raise ZeroDivisionError("Деление на ноль")
        n = self.numerator * o.denominator
        d = self.denominator * o.numerator
        return TFrac(f"{n}/{d}")

    def equals(self, other: TANumber) -> bool:
        o = TFrac(str(other))
        return self.numerator == o.numerator and self.denominator == o.denominator

    def sqr(self) -> "TFrac":
        n = self.numerator**2
        d = self.denominator**2
        return TFrac(f"{n}/{d}")

    def inv(self) -> "TFrac":
        if self.is_zero():
            raise ZeroDivisionError("Обратная дробь к нулю не существует")
        return TFrac(f"{self.denominator}/{self.numerator}")


@dataclass
class TComp(TANumber):
    """
    TComp – комплексное число. [file:1]
    Формат строки: "a i* b" (как в примере C++: cCSeparator = " i* "). [file:1]
    """

    re: TPNumber = field(default_factory=lambda: TPNumber(ZERO_STRING))  # Исправлено: default_factory
    im: TPNumber = field(default_factory=lambda: TPNumber(ZERO_STRING))  # Исправлено: default_factory

    COMPLEX_SEPARATOR = " i* "

    def __init__(self, value: str = ZERO_STRING) -> None:
        super().__init__(value)
        if value != ZERO_STRING:
            self._parse_from_string(value)

    # Внутренние методы

    def _parse_from_string(self, s: str) -> None:
        if self.COMPLEX_SEPARATOR in s:
            re_s, im_s = s.split(self.COMPLEX_SEPARATOR, 1)
            self.re = TPNumber(re_s)
            self.im = TPNumber(im_s)
        else:
            self.re = TPNumber(s)
            self.im = TPNumber(ZERO_STRING)
        self._update_string()

    def _update_string(self) -> None:
        self.string = f"{self.re.string}{self.COMPLEX_SEPARATOR}{self.im.string}"

    # Реализация абстрактных методов

    def is_zero(self) -> bool:
        return self.re.is_zero() and self.im.is_zero()

    def copy(self) -> "TComp":
        return TComp(self.string)

    def add(self, other: TANumber) -> "TComp":
        o = TComp(str(other))
        re = self.re.add(o.re)
        im = self.im.add(o.im)
        return TComp(f"{re.string}{self.COMPLEX_SEPARATOR}{im.string}")

    def sub(self, other: TANumber) -> "TComp":
        o = TComp(str(other))
        re = self.re.sub(o.re)
        im = self.im.sub(o.im)
        return TComp(f"{re.string}{self.COMPLEX_SEPARATOR}{im.string}")

    def mul(self, other: TANumber) -> "TComp":
        o = TComp(str(other))
        a, b = self.re._to_float(), self.im._to_float()
        c, d = o.re._to_float(), o.im._to_float()
        re_val = a * c - b * d
        im_val = a * d + b * c
        re_new = TPNumber(str(re_val))
        im_new = TPNumber(str(im_val))
        return TComp(f"{re_new.string}{self.COMPLEX_SEPARATOR}{im_new.string}")

    def div(self, other: TANumber) -> "TComp":
        o = TComp(str(other))
        a, b = self.re._to_float(), self.im._to_float()
        c, d = o.re._to_float(), o.im._to_float()
        denom = c * c + d * d
        if denom == 0.0:
            raise ZeroDivisionError("Деление на ноль")
        re_val = (a * c + b * d) / denom
        im_val = (b * c - a * d) / denom
        re_new = TPNumber(str(re_val))
        im_new = TPNumber(str(im_val))
        return TComp(f"{re_new.string}{self.COMPLEX_SEPARATOR}{im_new.string}")

    def equals(self, other: TANumber) -> bool:
        o = TComp(str(other))
        return self.re.equals(o.re) and self.im.equals(o.im)

    def sqr(self) -> "TComp":
        return self.mul(self)

    def inv(self) -> "TComp":
        if self.is_zero():
            raise ZeroDivisionError("Обратное к нулю комплексное число не существует")
        one = TComp("1 i* 0")
        return one.div(self)
