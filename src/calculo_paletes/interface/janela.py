"""Janela principal: cabeçalho (logo, título, versão) e as abas CHAPA, TRAPÉZIO e PESO DO PALETE."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGridLayout, QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget

from calculo_paletes import __version__
from calculo_paletes.interface.abas import AbaPalete, AbaPesoPalete
from calculo_paletes.interface.componentes import instalar_filtro_roda
from calculo_paletes.interface.estilo import ESTILO
from calculo_paletes.regras.valores_fixos import ValoresFixos

TITULO = "CÁLCULO DE PALETES"


class JanelaPrincipal(QMainWindow):
    def __init__(self, fixos: ValoresFixos | None = None, logo: Path | None = None) -> None:
        super().__init__()
        instalar_filtro_roda()  # roda do mouse só rola a tela (nunca troca de aba)
        self.setWindowTitle(f"Cálculo de Paletes — MG Centro de Serviços — versão {__version__}")
        self.setStyleSheet(ESTILO)
        fixos = fixos or ValoresFixos()

        self.aba_chapa = AbaPalete.chapa(fixos)
        self.aba_trapezio = AbaPalete.trapezio(fixos)
        self.aba_peso = AbaPesoPalete(fixos)
        self.abas = QTabWidget()
        self.abas.addTab(self.aba_chapa, "CHAPA")
        self.abas.addTab(self.aba_trapezio, "TRAPÉZIO")
        self.abas.addTab(self.aba_peso, "PESO DO PALETE")

        tela = QVBoxLayout()
        tela.setContentsMargins(16, 12, 16, 16)
        tela.setSpacing(12)
        tela.addLayout(self._cabecalho(logo))
        tela.addWidget(self.abas, 1)
        central = QWidget(objectName="central")
        central.setLayout(tela)
        self.setCentralWidget(central)
        # Mede as abas já agora: sem isso o showMaximized() pode se perder (janela pequena).
        self.ensurePolished()
        central.layout().activate()

    def _cabecalho(self, logo: Path | None) -> QGridLayout:
        """Logo à esquerda, título centralizado na largura toda e versão à direita."""
        imagem = QLabel()
        if logo is not None:
            imagem.setPixmap(QPixmap(str(logo)).scaledToHeight(70, Qt.SmoothTransformation))
        grade = QGridLayout()
        grade.addWidget(imagem, 0, 0, Qt.AlignLeft | Qt.AlignVCenter)
        grade.addWidget(QLabel(TITULO, objectName="titulo"), 0, 1, Qt.AlignCenter)
        versao = QLabel(f"versão {__version__}", objectName="versao")
        grade.addWidget(versao, 0, 2, Qt.AlignRight | Qt.AlignTop)
        grade.setColumnStretch(0, 1)
        grade.setColumnStretch(2, 1)  # colunas laterais iguais → título no centro
        return grade

    def usar_fixos(self, fixos: ValoresFixos) -> None:
        """Novos valores fixos (menu EDITAR, Fase 3): todas as abas refazem as contas."""
        for aba in (self.aba_chapa, self.aba_trapezio, self.aba_peso):
            aba.usar_fixos(fixos)
