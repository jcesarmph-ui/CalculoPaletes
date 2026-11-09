"""Testes da janela: digita como o usuário e confere o que aparece (números fictícios)."""

import pytest

from calculo_paletes import __version__
from calculo_paletes.interface.abas import SEM_RESULTADO
from calculo_paletes.interface.janela import JanelaPrincipal
from calculo_paletes.interface.numeros import formatar, ler_numero
from calculo_paletes.regras.valores_fixos import ValoresFixos


@pytest.fixture
def janela(app):
    j = JanelaPrincipal()
    yield j
    j.close()


def digitar(aba, valores: dict[str, str]) -> None:
    """Escreve nos campos e avisa a aba, como acontece a cada tecla."""
    for nome, texto in valores.items():
        aba.campos[nome].setText(texto)
    aba.recalcular()


CHAPA_FICTICIA = {
    "espessura": "1,5",
    "largura": "1200",
    "comprimento": "2000",
    "quantidade_kg": "3000",
    "quantidade_pilhas": "2",
    "largura_palete": "1250",
    "comprimento_palete": "2050",
}


def test_titulo_e_versao(janela):
    assert __version__ in janela.windowTitle()
    assert [janela.abas.tabText(i) for i in range(3)] == ["CHAPA", "TRAPÉZIO", "PESO DO PALETE"]


def test_aba_chapa_calcula_enquanto_digita(janela):
    aba = janela.aba_chapa
    digitar(aba, CHAPA_FICTICIA)
    textos = {nome: rotulo.text() for nome, rotulo in aba.saidas.items()}
    assert textos == {
        "blanks_por_pilha": "54",
        "altura_pilha": "81,00",
        "altura_total": "211,00",
        "fita_transversal": "3022,00",
        "fita_longitudinal": "4362,00",
        "largura_plastico": "1331,00",
        "comprimento_plastico": "4262,00",
    }
    assert aba.saidas["altura_total"].property("calculado") is True  # borda verde
    assert aba.avisos.text() == ""


def test_campo_vazio_mostra_dica_e_nenhum_resultado(janela):
    aba = janela.aba_chapa
    digitar(aba, {**CHAPA_FICTICIA, "quantidade_pilhas": ""})
    assert aba.saidas["blanks_por_pilha"].text() == SEM_RESULTADO
    assert aba.saidas["blanks_por_pilha"].property("calculado") is False
    assert "Preencha todos os campos" in aba.avisos.text()
    assert aba.avisos.objectName() == "dica"


def test_erro_de_digitacao_aparece_em_vermelho_dizendo_a_caixa(janela):
    aba = janela.aba_chapa
    digitar(aba, {**CHAPA_FICTICIA, "largura_palete": "12a0"})
    assert aba.avisos.objectName() == "erro"
    assert "Largura (palete)" in aba.avisos.text()
    assert aba.saidas["fita_transversal"].text() == SEM_RESULTADO


def test_valor_zerado_mostra_mensagem_da_regra(janela):
    aba = janela.aba_chapa
    digitar(aba, {**CHAPA_FICTICIA, "espessura": "0"})
    assert aba.avisos.objectName() == "erro"
    assert "espessura precisa ser maior que zero" in aba.avisos.text()


def test_aba_trapezio(janela):
    aba = janela.aba_trapezio
    digitar(
        aba,
        {
            "espessura": "2",
            "base_menor": "500",
            "base_maior": "900",
            "altura_trapezio": "600",
            "quantidade_kg": "4000",
            "quantidade_pilhas": "2",
            "largura_palete": "950",
            "comprimento_palete": "1400",
        },
    )
    assert aba.saidas["blanks_por_pilha"].text() == "304"
    assert aba.saidas["fita_transversal"].text() == "3476,00"
    assert aba.saidas["comprimento_plastico"].text() == "4016,00"


def test_trapezio_com_bases_invertidas_da_erro(janela):
    aba = janela.aba_trapezio
    digitar(
        aba,
        {
            "espessura": "2",
            "base_menor": "900",
            "base_maior": "500",
            "altura_trapezio": "600",
            "quantidade_kg": "4000",
            "quantidade_pilhas": "2",
            "largura_palete": "950",
            "comprimento_palete": "1400",
        },
    )
    assert "base menor não pode ser maior" in aba.avisos.text()


def test_peso_do_palete_usa_so_as_linhas_preenchidas(janela):
    aba = janela.aba_peso
    digitar(aba, {"medida_1": "1200", "quantidade_1": "3", "medida_3": "900", "quantidade_3": "4"})
    assert aba.peso.text() == "16,96"  # 16,956 kg
    assert aba.peso.property("calculado") is True


def test_peso_linha_pela_metade_avisa_o_numero_da_linha(janela):
    aba = janela.aba_peso
    digitar(aba, {"medida_2": "1200"})
    assert aba.avisos.objectName() == "erro"
    assert "Linha 2: preencha a medida e a quantidade" in aba.avisos.text()
    assert aba.peso.text() == SEM_RESULTADO


def test_valores_fixos_aparecem_na_tela(janela):
    assert janela.aba_chapa.textos_fixos["densidade_aco"].text() == "7,85 g/cm³"
    assert janela.aba_chapa.textos_fixos["altura_palete"].text() == "130 mm"
    assert janela.aba_peso.textos_fixos["cava"].text() == "10 × 30 mm"
    assert janela.aba_peso.textos_fixos["area_util"].text() == "3925 mm²"


def test_trocar_valores_fixos_refaz_as_contas(janela):
    digitar(janela.aba_chapa, CHAPA_FICTICIA)
    janela.usar_fixos(ValoresFixos(altura_madeira=90, quantidade_madeiras=1))
    assert janela.aba_chapa.saidas["altura_total"].text() == "171,00"  # 81 + 90
    assert janela.aba_chapa.textos_fixos["altura_palete"].text() == "90 mm"


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [("1,5", 1.5), ("1.5", 1.5), (" 1200 ", 1200.0), (",5", 0.5), ("", None), ("  ", None)],
)
def test_ler_numero_aceita_virgula_e_ponto(texto, esperado):
    assert ler_numero(texto, "Campo") == esperado


@pytest.mark.parametrize("texto", ["1.504,5", "abc", "12a0", "1,2,3"])
def test_ler_numero_recusa_texto_invalido(texto):
    with pytest.raises(ValueError, match="não é um número"):
        ler_numero(texto, "Campo")


def test_formatar_usa_virgula():
    assert formatar(3596.16) == "3596,16"
    assert formatar(54, 0) == "54"


def test_janela_cabe_numa_tela_full_hd(janela):
    """Tela 1920×1080 tem ~1032 px livres (barra de tarefas) menos ~30 da barra de título."""
    for indice in range(janela.abas.count()):
        janela.abas.setCurrentIndex(indice)
        assert janela.minimumSizeHint().height() <= 1000
        assert janela.minimumSizeHint().width() <= 1920


def test_numero_enorme_nao_mexe_na_tela(app):
    """Teste do usuário: número "infinito" num campo não pode mover nada na tela."""
    from PySide6.QtCore import Qt

    from calculo_paletes.interface.componentes import GRANDE_DEMAIS, MAXIMO_CARACTERES

    j = JanelaPrincipal()
    j.setAttribute(Qt.WA_DontShowOnScreen)
    j.resize(1920, 1000)
    j.show()
    for indice, aba in enumerate((j.aba_chapa, j.aba_trapezio, j.aba_peso)):
        j.abas.setCurrentIndex(indice)
        app.processEvents()
        antes = {nome: campo.geometry() for nome, campo in aba.campos.items()}
        for campo in aba.campos.values():
            campo.setText("9" * 50)  # o campo corta no limite
            assert len(campo.text()) == MAXIMO_CARACTERES
        aba.recalcular()
        app.processEvents()
        assert {nome: campo.geometry() for nome, campo in aba.campos.items()} == antes
        assert j.size().width() == 1920
    assert j.aba_peso.peso.text() == GRANDE_DEMAIS
    assert j.aba_peso.peso.toolTip()  # o número inteiro fica na dica do mouse
    j.close()


def test_numero_enorme_calculado_com_a_aba_escondida(app):
    """Conta refeita com a aba escondida (ex.: Salvar no EDITAR): ao abrir a aba, mostra
    "grande demais" e não o número cortado."""
    from PySide6.QtCore import Qt

    from calculo_paletes.interface.componentes import GRANDE_DEMAIS

    j = JanelaPrincipal()
    j.setAttribute(Qt.WA_DontShowOnScreen)
    j.resize(1920, 1000)
    j.show()
    app.processEvents()
    j.abas.setCurrentIndex(0)  # aba PESO DO PALETE escondida
    for campo in j.aba_peso.campos.values():
        campo.setText("9" * 12)
    j.aba_peso.recalcular()
    j.abas.setCurrentIndex(2)
    app.processEvents()
    assert j.aba_peso.peso.text() == GRANDE_DEMAIS
    j.close()
