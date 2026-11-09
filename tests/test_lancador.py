"""Testes do lançador (cópia do programa para o PC), com pastas temporárias."""

from calculo_paletes import lancador


def _programa_falso(pasta, versao="1.0.0_20261110-090000"):
    programa = pasta / "programa"
    programa.mkdir()
    (programa / "versao.txt").write_text(versao, encoding="utf-8")
    (programa / lancador.NOME_EXE).write_text("exe", encoding="utf-8")
    return programa, versao


def test_copia_o_programa_inteiro_e_marca_pronto(tmp_path):
    programa, versao = _programa_falso(tmp_path)
    cache = tmp_path / "cache"
    destino = lancador.copiar_para_o_pc(programa, cache, versao)
    assert (destino / lancador.NOME_EXE).is_file()
    assert lancador.copia_pronta(cache, versao)
    assert lancador.versao_da_rede(programa) == versao


def test_segunda_abertura_nao_copia_de_novo(tmp_path):
    programa, versao = _programa_falso(tmp_path)
    cache = tmp_path / "cache"
    destino = lancador.copiar_para_o_pc(programa, cache, versao)
    (programa / lancador.NOME_EXE).write_text("mudou na rede", encoding="utf-8")
    lancador.copiar_para_o_pc(programa, cache, versao)  # mesma versão: usa a cópia que já existe
    assert (destino / lancador.NOME_EXE).read_text(encoding="utf-8") == "exe"


def test_copia_pela_metade_e_refeita(tmp_path):
    programa, versao = _programa_falso(tmp_path)
    cache = tmp_path / "cache"
    (cache / versao).mkdir(parents=True)  # sobra sem o arquivo de "pronto"
    destino = lancador.copiar_para_o_pc(programa, cache, versao)
    assert (destino / lancador.NOME_EXE).is_file()


def test_versao_nova_apaga_as_antigas(tmp_path):
    cache = tmp_path / "cache"
    for nome in ("0.9.0_antiga", "1.0.0_atual"):
        (cache / nome).mkdir(parents=True)
    lancador.limpar_versoes_antigas(cache, "1.0.0_atual")
    assert [p.name for p in cache.iterdir()] == ["1.0.0_atual"]
