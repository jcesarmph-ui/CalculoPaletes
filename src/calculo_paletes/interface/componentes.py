"""Comportamentos da tela que valem para o programa inteiro (padrão de todos os programas da MG)."""

from PySide6.QtCore import QEvent, QObject, QSize, Qt
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QTabBar,
)

GRANDE_DEMAIS = "grande demais"


class RotuloResultado(QLabel):
    """Caixa de resultado com tamanho que vem da tela, nunca do número.

    Um número enorme não alarga a caixa (o que empurrava a tela toda): se não couber, mostra
    "grande demais" em amarelo (aviso) e o número inteiro fica na dica do mouse.
    """

    def __init__(self, nome_estilo: str, texto: str = "") -> None:
        super().__init__(objectName=nome_estilo, alignment=Qt.AlignRight | Qt.AlignVCenter)
        # Ignored = o layout não olha o tamanho do texto; Fixed = altura de uma linha.
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self._completo = ""
        self.setText(texto)

    def minimumSizeHint(self) -> QSize:  # noqa: N802 — nome exigido pelo Qt
        return QSize(0, super().minimumSizeHint().height())

    def sizeHint(self) -> QSize:  # noqa: N802 — nome exigido pelo Qt
        return QSize(0, super().sizeHint().height())

    def setText(self, texto: str) -> None:  # noqa: N802 — nome exigido pelo Qt
        self._completo = texto
        self._ajustar()

    def texto_completo(self) -> str:
        return self._completo

    def resizeEvent(self, evento) -> None:  # noqa: N802 — nome exigido pelo Qt
        super().resizeEvent(evento)
        self._ajustar()

    def showEvent(self, evento) -> None:  # noqa: N802 — nome exigido pelo Qt
        # A conta pode ter sido refeita com a aba escondida (ex.: Salvar no EDITAR refaz as três
        # abas): ao aparecer, confere de novo se o número cabe.
        super().showEvent(evento)
        self._ajustar()

    def _ajustar(self) -> None:
        cabe = self.fontMetrics().horizontalAdvance(self._completo) <= self.contentsRect().width()
        estouro = bool(self._completo) and not cabe and self.isVisible()
        super().setText(GRANDE_DEMAIS if estouro else self._completo)
        self.setToolTip(self._completo if estouro else "")
        if self.property("estouro") != estouro:
            self.setProperty("estouro", estouro)
            self.style().unpolish(self)
            self.style().polish(self)


class TextoQuebrado(QLabel):
    """Texto de várias linhas (avisos) que quebra em vez de alargar a caixa."""

    def __init__(self) -> None:
        super().__init__(wordWrap=True, alignment=Qt.AlignTop | Qt.AlignLeft)
        # Ignored na largura: o texto se ajusta à caixa, nunca o contrário. Palavras enormes
        # não acontecem porque os campos aceitam no máximo MAXIMO_CARACTERES.
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)


# Mais que qualquer medida real (12 algarismos em mm passam de 999 km).
MAXIMO_CARACTERES = 12


def preparar_campo(campo: QLineEdit) -> None:
    """Limite de caracteres em todo campo de digitação (o texto nunca alarga a tela)."""
    campo.setMaxLength(MAXIMO_CARACTERES)


class FiltroRodaDoMouse(QObject):
    """A roda do mouse só rola a tela: nunca troca a opção de uma lista, número ou aba.

    Também põe a mãozinha do mouse em tudo o que é clicável (desligado fica com a seta).
    """

    SEM_RODA = (QComboBox, QAbstractSpinBox, QTabBar)
    CLICAVEIS = (QAbstractButton, QComboBox, QTabBar)

    def eventFilter(self, objeto, evento) -> bool:  # noqa: N802 — nome exigido pelo Qt
        if evento.type() in (QEvent.Polish, QEvent.EnabledChange) and isinstance(
            objeto, self.CLICAVEIS
        ):
            objeto.setCursor(Qt.PointingHandCursor if objeto.isEnabled() else Qt.ArrowCursor)
        if evento.type() == QEvent.Wheel and isinstance(objeto, self.SEM_RODA):
            pai = objeto.parentWidget()
            if pai is not None:
                QApplication.sendEvent(pai, evento)
            return True
        return False


def instalar_filtro_roda() -> None:
    """Liga o filtro para o programa inteiro (janelas e diálogos), uma vez só."""
    app = QApplication.instance()
    if app is not None and not hasattr(app, "_filtro_roda"):
        app._filtro_roda = FiltroRodaDoMouse(app)
        app.installEventFilter(app._filtro_roda)
