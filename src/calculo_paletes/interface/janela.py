"""Janela principal: cabeçalho (☰, logo, título, versão) e as abas CHAPA, TRAPÉZIO e PESO.

O ☰ abre o menu lateral; a opção EDITAR abre a edição dos valores fixos.
"""

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from calculo_paletes import __version__
from calculo_paletes.armazenamento.configuracao import Configuracao, ErroConfiguracao
from calculo_paletes.interface.abas import AbaPalete, AbaPesoPalete
from calculo_paletes.interface.componentes import instalar_filtro_roda
from calculo_paletes.interface.dialogos import DialogoEditar
from calculo_paletes.interface.estilo import ESTILO
from calculo_paletes.interface.menu import MenuLateral
from calculo_paletes.regras.valores_fixos import ValoresFixos

TITULO = "CÁLCULO DE PALETES"
ESPACO_MENU_LOGO = 28  # px entre o ☰ e o logo


class JanelaPrincipal(QMainWindow):
    def __init__(
        self,
        fixos: ValoresFixos | None = None,
        logo: Path | None = None,
        configuracao: Configuracao | None = None,
    ) -> None:
        super().__init__()
        instalar_filtro_roda()  # roda do mouse só rola a tela (nunca troca de aba)
        self.setWindowTitle(f"Cálculo de Paletes — MG Centro de Serviços — versão {__version__}")
        self.setStyleSheet(ESTILO)
        self.fixos = fixos or ValoresFixos()
        self.configuracao = configuracao
        # Quem mostra as janelas do EDITAR (os testes trocam para não ficar esperando clique).
        self.executar_dialogo: Callable[[QDialog], int] = lambda dialogo: dialogo.exec()

        self.aba_chapa = AbaPalete.chapa(self.fixos)
        self.aba_trapezio = AbaPalete.trapezio(self.fixos)
        self.aba_peso = AbaPesoPalete(self.fixos)
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

        self.menu = MenuLateral(central)
        self.menu.editar.connect(self.abrir_editar)
        self.botao_menu.clicked.connect(self.menu.alternar)
        # Mede as abas já agora: sem isso o showMaximized() pode se perder (janela pequena).
        self.ensurePolished()
        central.layout().activate()

    def _cabecalho(self, logo: Path | None) -> QGridLayout:
        """☰ e logo à esquerda, título centralizado na largura toda e versão à direita."""
        self.botao_menu = QPushButton("☰", objectName="botao_menu")
        self.botao_menu.setToolTip("Menu")
        imagem = QLabel()
        if logo is not None:
            imagem.setPixmap(QPixmap(str(logo)).scaledToHeight(70, Qt.SmoothTransformation))
        esquerda = QHBoxLayout()
        esquerda.setSpacing(ESPACO_MENU_LOGO)
        esquerda.addWidget(self.botao_menu, 0, Qt.AlignVCenter)
        esquerda.addWidget(imagem, 0, Qt.AlignVCenter)
        esquerda.addStretch(1)

        grade = QGridLayout()
        grade.addLayout(esquerda, 0, 0)
        grade.addWidget(QLabel(TITULO, objectName="titulo"), 0, 1, Qt.AlignCenter)
        versao = QLabel(f"versão {__version__}", objectName="versao")
        grade.addWidget(versao, 0, 2, Qt.AlignRight | Qt.AlignTop)
        grade.setColumnStretch(0, 1)
        grade.setColumnStretch(2, 1)  # colunas laterais iguais → título no centro
        return grade

    def resizeEvent(self, evento) -> None:  # noqa: N802 — nome exigido pelo Qt
        super().resizeEvent(evento)
        if self.menu.isVisible():
            self.menu.abrir()  # acompanha o novo tamanho da janela

    # ------------------------------------------------------------ EDITAR

    def abrir_editar(self) -> None:
        """Janela de edição → Salvar grava e as três abas refazem as contas."""
        if self.configuracao is None:
            return
        try:
            # Relê o arquivo: outra pessoa pode ter salvo algo desde que o programa abriu.
            atuais = self.configuracao.carregar_fixos()
        except ErroConfiguracao:
            atuais = self.fixos
        dialogo = DialogoEditar(self, self.configuracao, atuais)
        if self.executar_dialogo(dialogo) == QDialog.Accepted and dialogo.salvos is not None:
            self.usar_fixos(dialogo.salvos)

    def usar_fixos(self, fixos: ValoresFixos) -> None:
        """Novos valores fixos: todas as abas refazem as contas."""
        self.fixos = fixos
        for aba in (self.aba_chapa, self.aba_trapezio, self.aba_peso):
            aba.usar_fixos(fixos)
