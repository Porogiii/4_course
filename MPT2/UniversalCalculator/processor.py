# processor.py
from __future__ import annotations
from enum import Enum, auto
from typing import Optional

from anumber import TANumber, TPNumber, TFrac, TComp, ZERO_STRING


class TOprtn(Enum):
    NONE = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DVD = auto()


class TFunc(Enum):
    REV = auto()
    SQR = auto()


class TProc:
    """
    Абстрактный тип данных «Процессор» (TProc). [file:1]
    Выполняет двухоперандные операции и однооперандные функции над TANumber.
    """

    def __init__(self, left: TANumber, right: TANumber) -> None:
        # Конструктор: копии операндов, Operation = None, Error = "". [file:1]
        self._lop_res: TANumber = left.copy()
        self._rop: TANumber = right.copy()
        self._operation: TOprtn = TOprtn.NONE
        self._error: str = ""

    # Свойства для доступа к полям [file:1]

    @property
    def lop_res(self) -> TANumber:
        """Читать левый операнд. [file:1]"""
        return self._lop_res.copy()

    @lop_res.setter
    def lop_res(self, operand: TANumber) -> None:
        """Записать левый операнд. [file:1]"""
        self._lop_res = operand.copy()

    @property
    def rop(self) -> TANumber:
        """Читать правый операнд. [file:1]"""
        return self._rop.copy()

    @rop.setter
    def rop(self, operand: TANumber) -> None:
        """Записать правый операнд. [file:1]"""
        self._rop = operand.copy()

    @property
    def operation(self) -> TOprtn:
        """Читать состояние (операцию). [file:1]"""
        return self._operation

    @operation.setter
    def operation(self, op: TOprtn) -> None:
        """Записать состояние (операцию). [file:1]"""
        self._operation = op

    @property
    def error(self) -> str:
        """Читать ошибку. [file:1]"""
        return self._error

    def clear_error(self) -> None:
        """Сброс ошибки. [file:1]"""
        self._error = ""

    # Основные операции [file:1]

    def reset(self) -> None:
        """Сброс процессора: оба операнда = 0, операция None, ошибка пустая. [file:1]"""
        self._lop_res = TPNumber(ZERO_STRING)
        self._rop = TPNumber(ZERO_STRING)
        self._operation = TOprtn.NONE
        self._error = ""

    def oprtn_clear(self) -> None:
        """Сброс операции. [file:1]"""
        self._operation = TOprtn.NONE

    def oprtn_run(self) -> None:
        """Выполнить текущую операцию над lop_res и rop. [file:1]"""
        if self._operation == TOprtn.NONE:
            return
        try:
            if self._operation == TOprtn.ADD:
                self._lop_res = self._lop_res.add(self._rop)
            elif self._operation == TOprtn.SUB:
                self._lop_res = self._lop_res.sub(self._rop)
            elif self._operation == TOprtn.MUL:
                self._lop_res = self._lop_res.mul(self._rop)
            elif self._operation == TOprtn.DVD:
                self._lop_res = self._lop_res.div(self._rop)
        except Exception as ex:
            self._error = str(ex)

    def func_run(self, func: TFunc) -> None:
        """Вычислить функцию над правым операндом. [file:1]"""
        try:
            if func == TFunc.REV:
                self._rop = self._rop.inv()
            elif func == TFunc.SQR:
                self._rop = self._rop.sqr()
        except Exception as ex:
            self._error = str(ex)
