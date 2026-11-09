"""Testes das fórmulas com números FICTÍCIOS (os da planilha real ficam em dados/testes/)."""

import pytest

from calculo_paletes.regras.calculos import (
    ErroEntrada,
    PecaMadeira,
    area_chapa,
    area_trapezio,
    calcular_palete,
    peso_palete,
)
from calculo_paletes.regras.valores_fixos import ValoresFixos

aprox = pytest.approx


# ---------------------------------------------------------------- chapa


def test_chapa_exemplo_do_claude_md():
    """Chapa 1,50 × 1200 × 2000, 3000 kg, 2 pilhas, palete 1250 × 2050 (conta feita à mão)."""
    r = calcular_palete(1.5, area_chapa(1200, 2000), 3000, 2, 1250, 2050)
    assert r.peso_blank == aprox(28.26)
    assert r.blanks_por_pilha == 54  # 53,08 arredondado para cima
    assert r.altura_pilha == aprox(81.0)  # 54 × 1,5 (usa o número já arredondado)
    assert r.altura_palete == aprox(130.0)  # 65 × 2
    assert r.altura_total == aprox(211.0)
    assert r.fita_transversal == aprox(3022.0)  # (211 + 1250) × 2 + 100
    assert r.fita_longitudinal == aprox(4362.0)  # (81 + 2050) × 2 + 100
    assert r.largura_plastico == aprox(1331.0)  # 1250 + 81
    assert r.comprimento_plastico == aprox(4262.0)  # 2050 × 2 + 81 × 2 (exato)


def test_blanks_exatos_nao_sobem_por_erro_de_virgula():
    """1 × 1000 × 1000 pesa 7,85 kg; 785 kg = 100 blanks certinhos, nunca 101."""
    r = calcular_palete(1, area_chapa(1000, 1000), 785, 1, 1000, 1000)
    assert r.blanks_por_pilha == 100


def test_qualquer_sobra_arredonda_para_cima():
    """Um pouco acima de 100 blanks já vira 101."""
    r = calcular_palete(1, area_chapa(1000, 1000), 785.1, 1, 1000, 1000)
    assert r.blanks_por_pilha == 101


# ---------------------------------------------------------------- trapézio


def test_trapezio_exemplo():
    """E 2,0; bases 500 e 900; altura 600; 4000 kg; 2 pilhas; palete 950 × 1400."""
    area = area_trapezio(500, 900, 600)
    assert area == aprox(420_000)  # (500 + 900) ÷ 2 × 600
    r = calcular_palete(2.0, area, 4000, 2, 950, 1400)
    assert r.peso_blank == aprox(6.594)
    assert r.blanks_por_pilha == 304  # 303,3 para cima
    assert r.altura_pilha == aprox(608.0)
    assert r.altura_total == aprox(738.0)
    assert r.fita_transversal == aprox(3476.0)
    assert r.fita_longitudinal == aprox(4116.0)
    assert r.largura_plastico == aprox(1558.0)
    assert r.comprimento_plastico == aprox(4016.0)


def test_trapezio_com_bases_iguais_e_um_retangulo():
    assert area_trapezio(800, 800, 500) == aprox(area_chapa(800, 500))


def test_trapezio_base_menor_maior_que_a_maior_da_erro():
    with pytest.raises(ErroEntrada, match="base menor não pode ser maior"):
        area_trapezio(900, 500, 600)


# ---------------------------------------------------------------- peso do palete


def test_peso_palete_exemplo():
    """1200 × 3 + 900 × 4 = 7200 mm de madeira × 3925 mm² × 0,6 / 1.000.000 = 16,956 kg."""
    linhas = [PecaMadeira(1200, 3), PecaMadeira(900, 4), None, None]
    assert peso_palete(linhas) == aprox(16.956)


def test_peso_palete_pula_linhas_vazias_no_meio():
    linhas = [None, PecaMadeira(1200, 3), None, PecaMadeira(900, 4)]
    assert peso_palete(linhas) == aprox(16.956)


def test_peso_palete_sem_linhas_e_zero():
    assert peso_palete([None, None, None, None]) == 0


def test_erro_do_peso_cita_o_numero_da_linha_da_tela():
    linhas = [None, None, PecaMadeira(0, 2), None]
    with pytest.raises(ErroEntrada, match="linha 3"):
        peso_palete(linhas)


def test_quantidade_de_madeira_quebrada_da_erro():
    with pytest.raises(ErroEntrada, match="inteiro"):
        peso_palete([PecaMadeira(1200, 2.5)])


# ---------------------------------------------------------------- valores fixos editados


def test_valores_fixos_padrao_sao_os_da_planilha():
    f = ValoresFixos()
    assert f.altura_palete == 130
    assert f.area_util_madeira == 3925  # 65×65 − 10×30
    assert f.densidade_aco_kg_mm3 == aprox(7.85e-6)
    assert f.densidade_madeira_kg_mm3 == aprox(0.6e-6)


def test_fixos_editados_mudam_as_contas():
    """Madeira de 90 em 1 camada e folga de 150: altura do palete 90 e fitas com +150."""
    fixos = ValoresFixos(altura_madeira=90, quantidade_madeiras=1, folga_fita=150)
    r = calcular_palete(1.5, area_chapa(1200, 2000), 3000, 2, 1250, 2050, fixos)
    assert r.altura_palete == 90
    assert r.altura_total == aprox(171.0)  # 81 + 90
    assert r.fita_transversal == aprox((171 + 1250) * 2 + 150)
    assert r.fita_longitudinal == aprox((81 + 2050) * 2 + 150)


def test_densidade_do_aco_editada_muda_o_numero_de_blanks():
    """Aço mais pesado → blank mais pesado → menos blanks para os mesmos kg."""
    mais_pesado = ValoresFixos(densidade_aco=8.0)
    r = calcular_palete(1.5, area_chapa(1200, 2000), 3000, 2, 1250, 2050, mais_pesado)
    assert r.peso_blank == aprox(28.8)
    assert r.blanks_por_pilha == 53  # 3000 ÷ 28,8 ÷ 2 = 52,08 → 53


# ---------------------------------------------------------------- valores inválidos


@pytest.mark.parametrize(
    ("argumentos", "trecho_da_mensagem"),
    [
        ((0, 1000, 785, 1, 1000, 1000), "espessura"),
        ((1, 1000, 0, 1, 1000, 1000), "quantidade a produzir"),
        ((1, 1000, 785, 0, 1000, 1000), "quantidade de pilhas"),
        ((1, 1000, 785, 1.5, 1000, 1000), "quantidade de pilhas"),
        ((1, 1000, 785, 1, -5, 1000), "largura do palete"),
        ((1, 1000, 785, 1, 1000, 0), "comprimento do palete"),
    ],
)
def test_valores_invalidos_dao_erro_em_portugues(argumentos, trecho_da_mensagem):
    with pytest.raises(ErroEntrada, match=trecho_da_mensagem):
        calcular_palete(*argumentos)


def test_largura_zerada_da_erro():
    with pytest.raises(ErroEntrada, match="largura"):
        area_chapa(0, 1000)
