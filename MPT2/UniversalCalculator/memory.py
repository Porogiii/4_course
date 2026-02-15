# memory.py
from __future__ import annotations
from enum import Enum
from typing import Optional

from anumber import TANumber, ZERO_STRING, TPNumber


class MemoryState(Enum):
    OFF = "_Off"
    ON = "_On"


class TMemory:
    """
    Абстрактный тип данных «память для Число» (TMemory). [file:1]
    Хранит ссылку на TANumber и состояние памяти.
    """

    def __init__(self, number: TANumber) -> None:
        # Конструктор: память выключена, хранится копия числа (0 по ТЗ). [file:1]
        self._mem_state = MemoryState.OFF
        self._mem: TANumber = number.copy()

    # Операции по спецификации [file:1]

    def mem_store(self, n: TANumber) -> None:
        """Записать (Store). [file:1]"""
        self._mem = n.copy()
        self._mem_state = MemoryState.ON

    def mem_restore(self) -> TANumber:
        """Взять (Restore). [file:1]"""
        # Возвращаем копию числа; состояние остаётся ON. [file:1]
        return self._mem.copy()

    def mem_add(self, n: TANumber) -> None:
        """Добавить (Add). [file:1]"""
        self._mem = self._mem.add(n)
        self._mem_state = MemoryState.ON

    def mem_clear(self) -> None:
        """Очистить (Clear). [file:1]"""
        self._mem = TPNumber(ZERO_STRING)
        self._mem_state = MemoryState.OFF

    # Свойства чтения состояния и числа [file:1]

    @property
    def mem_on(self) -> str:
        """ЧитатьСостояниеПамяти: String. [file:1]"""
        return self._mem_state.value

    @property
    def number(self) -> str:
        """ЧитатьЧисло: String. [file:1]"""
        return self._mem.string
