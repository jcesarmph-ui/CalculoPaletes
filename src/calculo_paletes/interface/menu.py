"""Menu lateral (☰): painel que abre por cima da tela, a partir da esquerda.

Por enquanto tem só a opção EDITAR. Clicar fora do painel, no ☰ de novo ou apertar Esc fecha.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

LARGURA_PAINEL = 320


class MenuLateral(QWidget):
    """Camada que cobre a janela: fundo escurecido + painel do menu à esquerda."""

    editar = Signal()

    def __init__(self, pai: QWidget) -> None:
        super().__init__(pai, objectName="fundo_menu")
        self.setAttribute(Qt.WA_StyledBackground, True)  # deixa o estilo pintar o fundo
        self.painel = QFrame(self, objectName="painel_menu")
        titulo = QLabel("MENU", objectName="titulo_menu")
        self.botao_editar = QPushButton("EDITAR", objectName="opcao_menu")
        self.botao_editar.setToolTip("Mudar os valores fixos usados nas contas")
        self.botao_editar.clicked.connect(self._escolheu_editar)

        layout = QVBoxLayout(self.painel)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(16)
        layout.addWidget(titulo)
        layout.addWidget(self.botao_editar)
        layout.addStretch(1)
        self.hide()

    def abrir(self) -> None:
        self.setGeometry(self.parentWidget().rect())  # cobre a janela inteira
        self.painel.setGeometry(0, 0, LARGURA_PAINEL, self.height())
        self.show()
        self.raise_()
        self.setFocus()

    def alternar(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.abrir()

    def _escolheu_editar(self) -> None:
        self.hide()
        self.editar.emit()

    def mousePressEvent(self, evento) -> None:  # noqa: N802 — nome exigido pelo Qt
        if not self.painel.geometry().contains(evento.position().toPoint()):
            self.hide()  # clicou fora do painel

    def keyPressEvent(self, evento) -> None:  # noqa: N802 — nome exigido pelo Qt
        if evento.key() == Qt.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(evento)
