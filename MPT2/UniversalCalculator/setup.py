# setup.py
from setuptools import setup, find_packages
import py2exe  # pip install pyinstaller (альтернатива)

from cx_Freeze import setup, Executable

# Зависимости
build_exe_options = {
    "packages": ["PyQt6", "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets", "PyQt6.QtWebEngineWidgets"],
    "include_files": ["help.html", "calculator.rc"],
    "excludes": ["tkinter"]
}

setup(
    name="UniversalCalculator",
    version="1.0",
    description="Универсальный калькулятор СибГУТИ",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py",
                           base="Win32GUI",  # Без консоли
                           icon="calculator.ico",  # Добавьте иконку
                           target_name="Калькулятор.exe")]
)
