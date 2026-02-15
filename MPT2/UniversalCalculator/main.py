# main.py
from ui_qt import TClcPnl

if __name__ == "__main__":
    # mode: "p" – p-ичные/вещественные, "f" – дроби, "c" – комплексные. [file:1]
    panel = TClcPnl(mode="p")
    panel.run()
