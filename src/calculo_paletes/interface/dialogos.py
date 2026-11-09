"""Janela do EDITAR: edição dos valores fixos (com Salvar e Cancelar)."""

from dataclasses import fields

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from calculo_paletes.armazenamento.configuracao import Configuracao
from calculo_paletes.interface.componentes import TextoQuebrado, preparar_campo
from calculo_paletes.interface.numeros import ler_numero
from calculo_paletes.regras.valores_fixos import DESCRICOES, ValoresFixos, problemas_dos_fixos


def _botoes(cancelar: QPushButton, confirmar: QPushButton) -> QHBoxLayout:
    linha = QHBoxLayout()
    linha.addStretch(1)
    linha.addWidget(cancelar)
    linha.addWidget(confirmar)
    return linha


def _mostrar_numero(valor: float) -> str:
    """7.85 → '7,85'; 65.0 → '65' (sem zeros sobrando no campo)."""
    return f"{valor:g}".replace(".", ",")


class DialogoEditar(QDialog):
    """Campos de todos os valores fixos. Salvar grava (vale para todos); Cancelar desiste."""

    def __init__(
        self, pai: QWidget | None, configuracao: Configuracao, atuais: ValoresFixos
    ) -> None:
        super().__init__(pai)
        self.configuracao = configuracao
        self.salvos: ValoresFixos | None = None  # preenchido quando Salvar dá certo
        self.setWindowTitle("EDITAR valores fixos")
        self.setModal(True)

        grade = QGridLayout()
        grade.setHorizontalSpacing(12)
        grade.setVerticalSpacing(10)
        self.campos: dict[str, QLineEdit] = {}
        for linha, campo in enumerate(fields(ValoresFixos)):
            descricao = DESCRICOES[campo.name]
            caixa_texto = QLineEdit(_mostrar_numero(getattr(atuais, campo.name)))
            caixa_texto.setAlignment(Qt.AlignRight)
            caixa_texto.setMinimumWidth(180)
            preparar_campo(caixa_texto)
            grade.addWidget(QLabel(descricao.rotulo), linha, 0)
            grade.addWidget(caixa_texto, linha, 1)
            grade.addWidget(QLabel(descricao.unidade, objectName="unidade"), linha, 2)
            self.campos[campo.name] = caixa_texto

        self.erro = TextoQuebrado()
        self.erro.setObjectName("erro")
        self.erro.setMinimumHeight(60)
        salvar = QPushButton("Salvar")
        salvar.setDefault(True)
        salvar.clicked.connect(self._salvar)
        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        layout.addWidget(
            QLabel("A mudança vale para todos que usam o programa.", objectName="dica")
        )
        layout.addLayout(grade)
        layout.addWidget(self.erro)
        layout.addLayout(_botoes(cancelar, salvar))

    def _ler_campos(self) -> tuple[dict[str, float], list[str]]:
        valores: dict[str, float] = {}
        erros: list[str] = []
        for nome, caixa_texto in self.campos.items():
            rotulo = DESCRICOES[nome].rotulo
            try:
                numero = ler_numero(caixa_texto.text(), rotulo)
            except ValueError as erro:
                erros.append(str(erro))
                continue
            if numero is None:
                erros.append(f"{rotulo}: preencha o valor.")
            else:
                valores[nome] = numero
        return valores, erros

    def _salvar(self) -> None:
        valores, erros = self._ler_campos()
        if not erros:
            madeiras = valores["quantidade_madeiras"]
            if madeiras == int(madeiras):
                valores["quantidade_madeiras"] = int(madeiras)  # grava "2", não "2.0"
            novos = ValoresFixos(**valores)
            erros = problemas_dos_fixos(novos)
        if erros:
            self.erro.setText("\n".join(erros))
            return
        try:
            self.configuracao.salvar_fixos(novos)
        except OSError as erro:
            self.erro.setText(f"Não foi possível gravar na pasta de dados: {erro}")
            return
        self.salvos = novos
        self.accept()
