"""Conversão entre o texto da tela e números (sem Qt, para testar sozinho).

Vírgula ou ponto são separador decimal; não há separador de milhar (largura 1504, não "1.504").
Os resultados são mostrados com vírgula, do jeito brasileiro.
"""

import re

_NUMERO = re.compile(r"-?(\d+([.,]\d+)?|[.,]\d+)")  # o "-" é lido para avisar "maior que zero"


def ler_numero(texto: str, rotulo: str) -> float | None:
    """Texto digitado → número; vazio → None. Erro de digitação → ValueError com o rótulo."""
    limpo = texto.strip()
    if not limpo:
        return None
    if not _NUMERO.fullmatch(limpo):
        raise ValueError(f"{rotulo}: '{limpo}' não é um número (use só algarismos e vírgula).")
    return float(limpo.replace(",", "."))


def formatar(valor: float, casas: int = 2) -> str:
    """3596.16 → '3596,16' (vírgula decimal, sem separador de milhar)."""
    return f"{valor:.{casas}f}".replace(".", ",")
