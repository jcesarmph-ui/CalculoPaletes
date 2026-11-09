"""As três abas da calculadora: CHAPA, TRAPÉZIO e PESO DO PALETE.

Cada aba é feita de faixas horizontais com caixas de mesma altura e largura:
entradas em cima, resultados no meio, avisos e valores fixos embaixo. As contas se refazem a
cada tecla digitada; nenhuma fórmula fica aqui (tudo vem de ``calculo_paletes.regras``).
"""

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from calculo_paletes.interface.componentes import (
    RotuloResultado,
    TextoQuebrado,
    preparar_campo,
)
from calculo_paletes.interface.numeros import formatar, ler_numero
from calculo_paletes.regras.calculos import (
    ErroEntrada,
    PecaMadeira,
    ResultadoPalete,
    area_chapa,
    area_trapezio,
    calcular_palete,
    peso_palete,
)
from calculo_paletes.regras.valores_fixos import ValoresFixos

SEM_RESULTADO = "—"
LINHAS_MADEIRA = 4


@dataclass(frozen=True)
class Campo:
    nome: str
    rotulo: str
    unidade: str
    dica: str = ""


@dataclass(frozen=True)
class Saida:
    nome: str  # atributo de ResultadoPalete
    rotulo: str
    unidade: str
    casas: int = 2


# ---------------------------------------------------------------- peças comuns


def _caixa(titulo: str) -> tuple[QGroupBox, QGridLayout]:
    caixa = QGroupBox(titulo)
    grade = QGridLayout(caixa)
    grade.setHorizontalSpacing(12)
    grade.setVerticalSpacing(12)
    grade.setColumnStretch(1, 1)
    return caixa, grade


def _faixa(*caixas: QWidget) -> QHBoxLayout:
    """Caixas lado a lado, todas com a mesma largura."""
    faixa = QHBoxLayout()
    faixa.setSpacing(12)
    for caixa in caixas:
        faixa.addWidget(caixa, 1)
    return faixa


def _marcar_calculado(rotulo: QLabel, calculado: bool) -> None:
    """Borda verde quando há resultado (o estilo lê a propriedade "calculado")."""
    rotulo.setProperty("calculado", calculado)
    rotulo.style().unpolish(rotulo)
    rotulo.style().polish(rotulo)


class _AbaBase(QWidget):
    """Parte comum: campos com Enter → próximo, caixa de avisos e caixa de valores fixos."""

    def __init__(self, fixos: ValoresFixos) -> None:
        super().__init__()
        self.fixos = fixos
        self.campos: dict[str, QLineEdit] = {}
        self.textos_fixos: dict[str, QLabel] = {}
        self.avisos = TextoQuebrado()

    def _novo_campo(self, grade: QGridLayout, linha: int, campo: Campo) -> QLineEdit:
        rotulo = QLabel(campo.rotulo)
        caixa_texto = QLineEdit()
        preparar_campo(caixa_texto)
        caixa_texto.setAlignment(Qt.AlignRight)
        if campo.dica:
            rotulo.setToolTip(campo.dica)
            caixa_texto.setToolTip(campo.dica)
        caixa_texto.textEdited.connect(self.recalcular)
        caixa_texto.returnPressed.connect(self._proximo_campo)
        grade.addWidget(rotulo, linha, 0)
        grade.addWidget(caixa_texto, linha, 1)
        grade.addWidget(QLabel(campo.unidade, objectName="unidade"), linha, 2)
        self.campos[campo.nome] = caixa_texto
        return caixa_texto

    def _proximo_campo(self) -> None:
        ordem = list(self.campos.values())
        atual = self.sender()
        if atual in ordem:
            ordem[(ordem.index(atual) + 1) % len(ordem)].setFocus()

    def _caixa_avisos(self) -> QGroupBox:
        caixa = QGroupBox("Avisos", objectName="rodape")
        layout = QVBoxLayout(caixa)
        layout.addWidget(self.avisos, 1)
        return caixa

    def _caixa_fixos(self, itens: list[tuple[str, str]]) -> QGroupBox:
        """Valores fixos só para informar (mudam no menu EDITAR, Fase 3)."""
        caixa, grade = _caixa("Valores fixos usados nas contas")
        caixa.setObjectName("rodape")
        grade.setVerticalSpacing(6)
        for linha, (chave, rotulo) in enumerate(itens):
            grade.addWidget(QLabel(rotulo), linha, 0)
            valor = QLabel(objectName="fixo", alignment=Qt.AlignRight)
            grade.addWidget(valor, linha, 1)
            self.textos_fixos[chave] = valor
        grade.setRowStretch(len(itens), 1)
        return caixa

    def _mostrar_dica(self, texto: str) -> None:
        self.avisos.setObjectName("dica")
        self.avisos.setText(texto)
        self.avisos.style().unpolish(self.avisos)
        self.avisos.style().polish(self.avisos)

    def _mostrar_erro(self, texto: str) -> None:
        self.avisos.setObjectName("erro")
        self.avisos.setText(texto)
        self.avisos.style().unpolish(self.avisos)
        self.avisos.style().polish(self.avisos)

    def usar_fixos(self, fixos: ValoresFixos) -> None:
        """Troca os valores fixos (menu EDITAR) e refaz as contas."""
        self.fixos = fixos
        self.recalcular()

    def recalcular(self) -> None:  # pragma: no cover — cada aba implementa
        raise NotImplementedError


# ---------------------------------------------------------------- chapa e trapézio

PRODUCAO = [
    Campo("quantidade_kg", "Quantidade a produzir", "kg"),
    Campo(
        "quantidade_pilhas", "Quantidade de pilhas", "un", "Em quantas pilhas o pedido é dividido"
    ),
]
PALETE = [
    Campo("largura_palete", "Largura", "mm", "Largura do palete de madeira"),
    Campo("comprimento_palete", "Comprimento", "mm", "Comprimento do palete de madeira"),
]
SAIDAS_PILHA = [
    Saida("blanks_por_pilha", "Blanks por pilha", "un", 0),
    Saida("altura_pilha", "Altura da pilha", "mm"),
    Saida("altura_total", "Altura total", "mm"),
]
SAIDAS_FITA = [
    Saida("fita_transversal", "Transversal", "mm"),
    Saida("fita_longitudinal", "Longitudinal", "mm"),
]
SAIDAS_PLASTICO = [
    Saida("largura_plastico", "Largura", "mm"),
    Saida("comprimento_plastico", "Comprimento", "mm"),
]

BLANK_CHAPA = [
    Campo("espessura", "Espessura", "mm"),
    Campo("largura", "Largura", "mm", "Largura do blank"),
    Campo("comprimento", "Comprimento", "mm", "Comprimento do blank"),
]
BLANK_TRAPEZIO = [
    Campo("espessura", "Espessura", "mm"),
    Campo("base_menor", "Base menor", "mm"),
    Campo("base_maior", "Base maior", "mm"),
    Campo("altura_trapezio", "Altura", "mm", "Altura do trapézio (distância entre as bases)"),
]


def _area_da_chapa(v: dict[str, float]) -> float:
    return area_chapa(v["largura"], v["comprimento"])


def _area_do_trapezio(v: dict[str, float]) -> float:
    return area_trapezio(v["base_menor"], v["base_maior"], v["altura_trapezio"])


class AbaPalete(_AbaBase):
    """Aba CHAPA ou TRAPÉZIO: mesmas entradas de produção/palete e mesmas saídas."""

    def __init__(
        self,
        fixos: ValoresFixos,
        campos_blank: list[Campo],
        area: Callable[[dict[str, float]], float],
    ) -> None:
        super().__init__(fixos)
        self._area = area
        self.saidas: dict[str, QLabel] = {}
        self.nomes_nos_avisos: dict[str, str] = {}

        entradas = _faixa(
            self._caixa_entradas("Blank", campos_blank),
            self._caixa_entradas("Produção", PRODUCAO),
            self._caixa_entradas("Palete", PALETE),
        )
        resultados = _faixa(
            self._caixa_saidas("Pilha", SAIDAS_PILHA),
            self._caixa_saidas("Fita", SAIDAS_FITA),
            self._caixa_saidas("Plástico", SAIDAS_PLASTICO),
        )
        rodape = _faixa(
            self._caixa_avisos(),
            self._caixa_fixos(
                [
                    ("densidade_aco", "Densidade do aço"),
                    ("altura_madeira", "Altura da madeira"),
                    ("quantidade_madeiras", "Madeiras empilhadas"),
                    ("altura_palete", "Altura do palete"),
                    ("folga_fita", "Folga da fita"),
                ]
            ),
        )
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addLayout(entradas, 1)
        layout.addLayout(resultados, 1)
        layout.addLayout(rodape, 1)
        self.recalcular()

    @classmethod
    def chapa(cls, fixos: ValoresFixos) -> "AbaPalete":
        return cls(fixos, BLANK_CHAPA, _area_da_chapa)

    @classmethod
    def trapezio(cls, fixos: ValoresFixos) -> "AbaPalete":
        return cls(fixos, BLANK_TRAPEZIO, _area_do_trapezio)

    def _caixa_entradas(self, titulo: str, campos: list[Campo]) -> QGroupBox:
        caixa, grade = _caixa(titulo)
        for linha, campo in enumerate(campos):
            self._novo_campo(grade, linha, campo)
            # "Largura" existe no blank e no palete: o aviso diz de qual caixa é.
            self.nomes_nos_avisos[campo.nome] = f"{campo.rotulo} ({titulo.lower()})"
        grade.setRowStretch(len(campos), 1)
        return caixa

    def _caixa_saidas(self, titulo: str, saidas: list[Saida]) -> QGroupBox:
        caixa, grade = _caixa(titulo)
        for linha, saida in enumerate(saidas):
            grade.addWidget(QLabel(saida.rotulo), linha, 0)
            valor = RotuloResultado("resultado", SEM_RESULTADO)
            grade.addWidget(valor, linha, 1)
            grade.addWidget(QLabel(saida.unidade, objectName="unidade"), linha, 2)
            self.saidas[saida.nome] = valor
        grade.setRowStretch(len(saidas), 1)
        return caixa

    def _atualizar_fixos(self) -> None:
        f = self.fixos
        self.textos_fixos["densidade_aco"].setText(f"{formatar(f.densidade_aco)} g/cm³")
        self.textos_fixos["altura_madeira"].setText(f"{formatar(f.altura_madeira, 0)} mm")
        self.textos_fixos["quantidade_madeiras"].setText(str(f.quantidade_madeiras))
        self.textos_fixos["altura_palete"].setText(f"{formatar(f.altura_palete, 0)} mm")
        self.textos_fixos["folga_fita"].setText(f"{formatar(f.folga_fita, 0)} mm")

    def _mostrar(self, resultado: ResultadoPalete | None) -> None:
        for todas in (SAIDAS_PILHA, SAIDAS_FITA, SAIDAS_PLASTICO):
            for saida in todas:
                rotulo = self.saidas[saida.nome]
                if resultado is None:
                    rotulo.setText(SEM_RESULTADO)
                else:
                    rotulo.setText(formatar(getattr(resultado, saida.nome), saida.casas))
                _marcar_calculado(rotulo, resultado is not None)

    def recalcular(self) -> None:
        self._atualizar_fixos()
        valores: dict[str, float] = {}
        erros: list[str] = []
        vazios = 0
        for nome, caixa_texto in self.campos.items():
            try:
                numero = ler_numero(caixa_texto.text(), self.nomes_nos_avisos[nome])
            except ValueError as erro:
                erros.append(str(erro))
                continue
            if numero is None:
                vazios += 1
            else:
                valores[nome] = numero

        if erros:
            self._mostrar(None)
            self._mostrar_erro("\n".join(erros))
            return
        if vazios:
            self._mostrar(None)
            self._mostrar_dica("Preencha todos os campos para ver o resultado.")
            return
        try:
            resultado = calcular_palete(
                valores["espessura"],
                self._area(valores),
                valores["quantidade_kg"],
                valores["quantidade_pilhas"],
                valores["largura_palete"],
                valores["comprimento_palete"],
                self.fixos,
            )
        except ErroEntrada as erro:
            self._mostrar(None)
            self._mostrar_erro(str(erro))
            return
        self._mostrar(resultado)
        self._mostrar_dica("")


# ---------------------------------------------------------------- peso do palete


class AbaPesoPalete(_AbaBase):
    """Aba PESO DO PALETE: até 4 linhas de medida × quantidade → peso em kg."""

    def __init__(self, fixos: ValoresFixos) -> None:
        super().__init__(fixos)
        self.medidas: list[QLineEdit] = []
        self.quantidades: list[QLineEdit] = []

        madeiras, grade = _caixa("Madeiras do palete")
        grade.addWidget(QLabel("Medida", objectName="unidade"), 0, 1, Qt.AlignCenter)
        grade.addWidget(QLabel("Quantidade", objectName="unidade"), 0, 3, Qt.AlignCenter)
        grade.setColumnStretch(3, 1)
        for i in range(LINHAS_MADEIRA):
            numero = i + 1
            grade.addWidget(QLabel(f"Linha {numero}"), numero, 0)
            medida = self._campo_tabela(f"medida_{numero}", "Comprimento da madeira")
            quantidade = self._campo_tabela(f"quantidade_{numero}", "Quantas madeiras")
            grade.addWidget(medida, numero, 1)
            grade.addWidget(QLabel("mm", objectName="unidade"), numero, 2)
            grade.addWidget(quantidade, numero, 3)
            grade.addWidget(QLabel("un", objectName="unidade"), numero, 4)
            self.medidas.append(medida)
            self.quantidades.append(quantidade)
        grade.setRowStretch(LINHAS_MADEIRA + 1, 1)

        caixa_peso = QGroupBox("Peso do palete")
        layout_peso = QVBoxLayout(caixa_peso)
        linha_peso = QHBoxLayout()
        self.peso = RotuloResultado("resultado_grande", SEM_RESULTADO)
        linha_peso.addWidget(self.peso, 1)
        linha_peso.addWidget(QLabel("kg", objectName="unidade"))
        layout_peso.addStretch(1)
        layout_peso.addLayout(linha_peso)
        dica = QLabel(
            "Preencha só as linhas que o palete usa; as vazias são ignoradas.",
            objectName="dica",
            wordWrap=True,
        )
        layout_peso.addWidget(dica)
        layout_peso.addStretch(1)

        rodape = _faixa(
            self._caixa_avisos(),
            self._caixa_fixos(
                [
                    ("densidade_madeira", "Densidade da madeira"),
                    ("secao_madeira", "Seção da madeira"),
                    ("cava", "Cava"),
                    ("area_util", "Área útil da seção"),
                ]
            ),
        )
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addLayout(_faixa(madeiras, caixa_peso), 2)
        layout.addLayout(rodape, 1)
        self.recalcular()

    def _campo_tabela(self, nome: str, dica: str) -> QLineEdit:
        caixa_texto = QLineEdit()
        preparar_campo(caixa_texto)
        caixa_texto.setAlignment(Qt.AlignRight)
        caixa_texto.setToolTip(dica)
        caixa_texto.textEdited.connect(self.recalcular)
        caixa_texto.returnPressed.connect(self._proximo_campo)
        self.campos[nome] = caixa_texto
        return caixa_texto

    def _atualizar_fixos(self) -> None:
        f = self.fixos
        self.textos_fixos["densidade_madeira"].setText(f"{formatar(f.densidade_madeira)} g/cm³")
        self.textos_fixos["secao_madeira"].setText(
            f"{formatar(f.secao_madeira_largura, 0)} × {formatar(f.secao_madeira_altura, 0)} mm"
        )
        self.textos_fixos["cava"].setText(
            f"{formatar(f.cava_largura, 0)} × {formatar(f.cava_altura, 0)} mm"
        )
        self.textos_fixos["area_util"].setText(f"{formatar(f.area_util_madeira, 0)} mm²")

    def _mostrar_peso(self, peso: float | None) -> None:
        self.peso.setText(SEM_RESULTADO if peso is None else formatar(peso))
        _marcar_calculado(self.peso, peso is not None)

    def recalcular(self) -> None:
        self._atualizar_fixos()
        linhas: list[PecaMadeira | None] = []
        erros: list[str] = []
        for i, (medida, quantidade) in enumerate(zip(self.medidas, self.quantidades, strict=True)):
            numero = i + 1
            try:
                valor_medida = ler_numero(medida.text(), f"Medida da linha {numero}")
                valor_qtd = ler_numero(quantidade.text(), f"Quantidade da linha {numero}")
            except ValueError as erro:
                erros.append(str(erro))
                linhas.append(None)
                continue
            if valor_medida is None and valor_qtd is None:
                linhas.append(None)
            elif valor_medida is None or valor_qtd is None:
                erros.append(f"Linha {numero}: preencha a medida e a quantidade.")
                linhas.append(None)
            else:
                linhas.append(PecaMadeira(valor_medida, valor_qtd))

        if erros:
            self._mostrar_peso(None)
            self._mostrar_erro("\n".join(erros))
            return
        if all(linha is None for linha in linhas):
            self._mostrar_peso(None)
            self._mostrar_dica("Preencha ao menos uma linha de madeira para ver o peso.")
            return
        try:
            peso = peso_palete(linhas, self.fixos)
        except ErroEntrada as erro:
            self._mostrar_peso(None)
            self._mostrar_erro(str(erro))
            return
        self._mostrar_peso(peso)
        self._mostrar_dica("")
