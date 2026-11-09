"""Arquivo ``configuracao.json`` na pasta de dados: os valores fixos editados no EDITAR.

É a única coisa que o programa grava (ele é só calculadora). Fica na pasta de dados da rede, ao
lado do ``.exe``, então vale para todos que usam o programa; nunca vai para o Git.

A gravação é feita num arquivo temporário e depois trocada de uma vez, para um programa que
feche no meio nunca deixar o arquivo pela metade.
"""

import json
import os
from dataclasses import asdict, fields
from pathlib import Path

from calculo_paletes.regras.valores_fixos import ValoresFixos, problemas_dos_fixos

NOME_ARQUIVO = "configuracao.json"


class ErroConfiguracao(Exception):
    """Arquivo de configuração ilegível ou inválido; a mensagem já vem pronta para a tela."""


class Configuracao:
    """Repositório da configuração (troque esta classe se um dia o lugar de guardar mudar)."""

    def __init__(self, pasta: Path) -> None:
        self.arquivo = Path(pasta) / NOME_ARQUIVO

    def _ler(self) -> dict:
        if not self.arquivo.is_file():
            return {}
        try:
            conteudo = json.loads(self.arquivo.read_text(encoding="utf-8"))
        except (OSError, ValueError) as erro:
            raise ErroConfiguracao(f"Não foi possível ler {self.arquivo.name}: {erro}") from erro
        if not isinstance(conteudo, dict):
            raise ErroConfiguracao(f"{self.arquivo.name} não está no formato esperado.")
        return conteudo

    def _gravar(self, conteudo: dict) -> None:
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        temporario = self.arquivo.with_suffix(".tmp")
        temporario.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temporario, self.arquivo)

    def carregar_fixos(self) -> ValoresFixos:
        """Valores fixos gravados; sem arquivo (ou sem valores), os padrões da planilha."""
        gravados = self._ler().get("valores_fixos", {})
        if not isinstance(gravados, dict):
            raise ErroConfiguracao("Os valores fixos gravados não estão no formato esperado.")
        conhecidos = {campo.name for campo in fields(ValoresFixos)}
        try:
            fixos = ValoresFixos(**{k: v for k, v in gravados.items() if k in conhecidos})
        except TypeError as erro:
            raise ErroConfiguracao(f"Valores fixos gravados inválidos: {erro}") from erro
        problemas = problemas_dos_fixos(fixos)
        if problemas:
            raise ErroConfiguracao("Valores fixos gravados inválidos:\n" + "\n".join(problemas))
        return fixos

    def salvar_fixos(self, fixos: ValoresFixos) -> None:
        """Grava os valores fixos; valem até alguém editar de novo."""
        problemas = problemas_dos_fixos(fixos)
        if problemas:
            raise ValueError("\n".join(problemas))
        self._gravar({"valores_fixos": asdict(fixos)})
