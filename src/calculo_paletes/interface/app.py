"""Abre o programa: ícone, logo e janela em tela cheia."""

import ctypes
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from calculo_paletes.interface.estilo import LOGOS
from calculo_paletes.interface.janela import JanelaPrincipal
from calculo_paletes.interface.pasta_dados import arquivo_se_existir, pasta_dados_padrao


def main() -> int:
    if sys.platform == "win32":
        # Sem isso o Windows agrupa a janela sob o python.exe e mostra o ícone do Python
        # na barra de tarefas.
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MG.CalculoPaletes")
    app = QApplication(sys.argv)
    pasta = pasta_dados_padrao()
    icone = arquivo_se_existir(pasta, "icone_mg.png")
    if icone is not None:
        app.setWindowIcon(QIcon(str(icone)))
    logo = next(filter(None, (arquivo_se_existir(pasta, nome) for nome in LOGOS)), None)
    janela = JanelaPrincipal(logo=logo)
    janela.showMaximized()
    return app.exec()
