"""Testes do arquivo de configuração (valores fixos) numa pasta temporária."""

import json

import pytest

from calculo_paletes.armazenamento.configuracao import Configuracao, ErroConfiguracao
from calculo_paletes.regras.valores_fixos import ValoresFixos, problemas_dos_fixos


def test_sem_arquivo_usa_os_valores_da_planilha(tmp_path):
    assert Configuracao(tmp_path).carregar_fixos() == ValoresFixos()


def test_salvar_e_carregar_de_volta(tmp_path):
    novos = ValoresFixos(densidade_aco=8.0, quantidade_madeiras=3, folga_fita=150)
    Configuracao(tmp_path).salvar_fixos(novos)
    assert Configuracao(tmp_path).carregar_fixos() == novos  # vale "para sempre"


def test_salvar_valor_invalido_e_recusado(tmp_path):
    with pytest.raises(ValueError, match="maior que zero"):
        Configuracao(tmp_path).salvar_fixos(ValoresFixos(densidade_aco=0))
    assert not (tmp_path / "configuracao.json").exists()


def test_arquivo_estragado_avisa_em_vez_de_quebrar(tmp_path):
    (tmp_path / "configuracao.json").write_text("{ isto não é json", encoding="utf-8")
    with pytest.raises(ErroConfiguracao, match="Não foi possível ler"):
        Configuracao(tmp_path).carregar_fixos()


def test_valor_gravado_invalido_avisa(tmp_path):
    conteudo = {"valores_fixos": {"altura_madeira": -5}}
    (tmp_path / "configuracao.json").write_text(json.dumps(conteudo), encoding="utf-8")
    with pytest.raises(ErroConfiguracao, match="Altura da madeira"):
        Configuracao(tmp_path).carregar_fixos()


@pytest.mark.parametrize(
    ("fixos", "trecho"),
    [
        (ValoresFixos(densidade_madeira=-1), "Densidade da madeira: precisa ser maior que zero"),
        (
            ValoresFixos(quantidade_madeiras=1.5),
            "Madeiras empilhadas: precisa ser um número inteiro",
        ),
        (ValoresFixos(quantidade_madeiras=0), "Madeiras empilhadas: precisa ser maior que zero"),
        (ValoresFixos(folga_fita=-1), "Folga da fita: precisa ser zero ou mais"),
        (ValoresFixos(cava_largura=65, cava_altura=65), "cava não pode ser do tamanho"),
    ],
)
def test_problemas_dos_fixos(fixos, trecho):
    assert any(trecho in problema for problema in problemas_dos_fixos(fixos))


def test_zero_de_folga_e_de_cava_e_permitido():
    """Zero quer dizer "não tem" (sem folga na fita, madeira sem cava)."""
    assert problemas_dos_fixos(ValoresFixos(folga_fita=0, cava_largura=0, cava_altura=0)) == []
