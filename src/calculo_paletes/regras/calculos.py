"""Fórmulas do palete de chapas e trapézios e do peso do palete de madeira.

Todas as medidas em mm e pesos em kg. As fórmulas seguem as células verdes da planilha original,
com duas decisões do usuário (2026-11-09):
- os blanks por pilha são **arredondados para cima** (não existe meio blank);
- a altura da pilha usa esse número **já arredondado**.
"""

import math
from collections.abc import Iterable
from dataclasses import dataclass

from calculo_paletes.regras.valores_fixos import ValoresFixos

# Casas usadas antes de arredondar para cima: evita que um resultado exato como 100 vire
# 100,00000000000001 (erro normal de conta com vírgula no computador) e suba para 101.
_CASAS_ANTES_DO_TETO = 9


class ErroEntrada(ValueError):
    """Valor digitado inválido; a mensagem já vem pronta para mostrar ao usuário."""


@dataclass(frozen=True)
class ResultadoPalete:
    """Saídas do cálculo de chapa ou trapézio (mm, exceto quando indicado)."""

    peso_blank: float  # kg
    blanks_por_pilha: int
    altura_pilha: float
    altura_palete: float
    altura_total: float
    fita_transversal: float
    fita_longitudinal: float
    largura_plastico: float
    comprimento_plastico: float


@dataclass(frozen=True)
class PecaMadeira:
    """Uma linha do peso do palete: medida (comprimento da madeira, mm) × quantidade."""

    medida: float
    quantidade: int


def _exigir_positivo(valor: float, nome: str) -> None:
    if valor <= 0:
        raise ErroEntrada(f"{nome} precisa ser maior que zero.")


def _exigir_inteiro_positivo(valor: float, nome: str) -> None:
    if valor != int(valor) or valor < 1:
        raise ErroEntrada(f"{nome} precisa ser um número inteiro, de 1 para cima.")


def area_chapa(largura: float, comprimento: float) -> float:
    """Área do blank retangular (mm²)."""
    _exigir_positivo(largura, "A largura")
    _exigir_positivo(comprimento, "O comprimento")
    return largura * comprimento


def area_trapezio(base_menor: float, base_maior: float, altura: float) -> float:
    """Área do blank trapezoidal (mm²) = (base menor + base maior) ÷ 2 × altura."""
    _exigir_positivo(base_menor, "A base menor")
    _exigir_positivo(base_maior, "A base maior")
    _exigir_positivo(altura, "A altura do trapézio")
    if base_menor > base_maior:
        raise ErroEntrada("A base menor não pode ser maior que a base maior.")
    return (base_menor + base_maior) / 2 * altura


def calcular_palete(
    espessura: float,
    area: float,
    quantidade_kg: float,
    quantidade_pilhas: int,
    largura_palete: float,
    comprimento_palete: float,
    fixos: ValoresFixos | None = None,
) -> ResultadoPalete:
    """Calcula pilhas, alturas, fita e plástico (serve para chapa e para trapézio).

    ``area`` vem de :func:`area_chapa` ou :func:`area_trapezio`.
    """
    fixos = fixos or ValoresFixos()
    _exigir_positivo(espessura, "A espessura")
    _exigir_positivo(area, "A área do blank")
    _exigir_positivo(quantidade_kg, "A quantidade a produzir")
    _exigir_inteiro_positivo(quantidade_pilhas, "A quantidade de pilhas")
    _exigir_positivo(largura_palete, "A largura do palete")
    _exigir_positivo(comprimento_palete, "O comprimento do palete")

    peso_blank = espessura * area * fixos.densidade_aco_kg_mm3
    blanks_quebrado = quantidade_kg / peso_blank / quantidade_pilhas
    blanks_por_pilha = math.ceil(round(blanks_quebrado, _CASAS_ANTES_DO_TETO))

    altura_pilha = blanks_por_pilha * espessura
    altura_palete = fixos.altura_palete
    altura_total = altura_pilha + altura_palete

    return ResultadoPalete(
        peso_blank=peso_blank,
        blanks_por_pilha=blanks_por_pilha,
        altura_pilha=altura_pilha,
        altura_palete=altura_palete,
        altura_total=altura_total,
        fita_transversal=(altura_total + largura_palete) * 2 + fixos.folga_fita,
        fita_longitudinal=(altura_pilha + comprimento_palete) * 2 + fixos.folga_fita,
        largura_plastico=largura_palete + altura_pilha,
        comprimento_plastico=comprimento_palete * 2 + altura_pilha * 2,
    )


def peso_palete(linhas: Iterable[PecaMadeira | None], fixos: ValoresFixos | None = None) -> float:
    """Peso do palete de madeira (kg) = Σ área útil × medida × quantidade × densidade.

    Recebe as linhas na ordem da tela (até 4); linha vazia vem como ``None`` e é pulada, para o
    aviso de erro citar o mesmo número de linha que o usuário vê. Sem nenhuma linha, o peso é zero.
    """
    fixos = fixos or ValoresFixos()
    total_mm = 0.0
    for numero, peca in enumerate(linhas, start=1):
        if peca is None:
            continue
        _exigir_positivo(peca.medida, f"A medida da linha {numero}")
        _exigir_inteiro_positivo(peca.quantidade, f"A quantidade da linha {numero}")
        total_mm += peca.medida * peca.quantidade
    return fixos.area_util_madeira * total_mm * fixos.densidade_madeira_kg_mm3
