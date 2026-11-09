"""Onde ficam os arquivos que não vão para o Git: logo, ícone e (Fase 3) os valores fixos."""

import os
import sys
from pathlib import Path


def pasta_dados_padrao() -> Path:
    """Procura a pasta de dados nesta ordem:
    1. variável de ambiente CALCULO_PALETES_DADOS;
    2. no `.exe` (PyInstaller marca `sys.frozen`): `dados/` ao lado do executável (pasta da rede);
    3. `dados/` na pasta atual; 4. `dados/` na pasta do projeto (desenvolvimento).
    """
    if os.environ.get("CALCULO_PALETES_DADOS"):
        return Path(os.environ["CALCULO_PALETES_DADOS"])
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "dados"
    if (Path.cwd() / "dados").is_dir():
        return Path.cwd() / "dados"
    return Path(__file__).resolve().parents[3] / "dados"


def arquivo_se_existir(pasta: Path, nome: str) -> Path | None:
    """Caminho do arquivo opcional (logo, ícone) ou None se não estiver lá."""
    caminho = pasta / nome
    return caminho if caminho.is_file() else None
