"""Testes do menu ☰ e do EDITAR (pasta de dados temporária; nada toca em dados/)."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QDialog

from calculo_paletes.armazenamento.configuracao import Configuracao
from calculo_paletes.interface.dialogos import DialogoEditar
from calculo_paletes.interface.janela import JanelaPrincipal
from calculo_paletes.regras.valores_fixos import ValoresFixos

CHAPA = {
    "espessura": "1,5",
    "largura": "1200",
    "comprimento": "2000",
    "quantidade_kg": "3000",
    "quantidade_pilhas": "2",
    "largura_palete": "1250",
    "comprimento_palete": "2050",
}


@pytest.fixture
def janela(app, tmp_path):
    j = JanelaPrincipal(configuracao=Configuracao(tmp_path))
    j.setAttribute(Qt.WA_DontShowOnScreen)
    j.resize(1920, 1000)
    j.show()
    app.processEvents()  # deixa a janela se arrumar no tamanho antes de medir os resultados
    for nome, texto in CHAPA.items():
        j.aba_chapa.campos[nome].setText(texto)
    j.aba_chapa.recalcular()
    yield j
    j.close()


def usar_dialogo(janela, acao):
    """Troca o "abrir e esperar o clique" por uma ação automática no diálogo."""
    vistos: list[QDialog] = []

    def executar(dialogo):
        vistos.append(dialogo)
        acao(dialogo)
        return dialogo.result()

    janela.executar_dialogo = executar
    return vistos


def test_botao_menu_abre_e_esc_fecha(janela):
    assert not janela.menu.isVisible()
    janela.botao_menu.click()
    assert janela.menu.isVisible()
    QApplication.sendEvent(janela.menu, QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier))
    assert not janela.menu.isVisible()


def test_editar_abre_direto_sem_senha(janela):
    vistos = usar_dialogo(janela, lambda d: d.reject())
    janela.menu.abrir()
    janela.menu.botao_editar.click()
    assert not janela.menu.isVisible()  # o menu fecha ao escolher
    assert len(vistos) == 1 and isinstance(vistos[0], DialogoEditar)


def test_salvar_grava_e_refaz_as_contas(janela, tmp_path):
    def mudar_folga(dialogo):
        dialogo.campos["folga_fita"].setText("150")
        dialogo._salvar()

    usar_dialogo(janela, mudar_folga)
    janela.abrir_editar()
    QApplication.processEvents()
    fita = janela.aba_chapa.saidas["fita_transversal"].texto_completo()
    assert fita == "3072,00"  # (211 + 1250) × 2 + 150
    assert janela.aba_chapa.textos_fixos["folga_fita"].text() == "150 mm"
    assert Configuracao(tmp_path).carregar_fixos().folga_fita == 150  # fica gravado


def test_cancelar_nao_muda_nada(janela, tmp_path):
    def mudar_e_cancelar(dialogo):
        dialogo.campos["folga_fita"].setText("150")
        dialogo.reject()

    usar_dialogo(janela, mudar_e_cancelar)
    janela.abrir_editar()
    QApplication.processEvents()
    assert janela.aba_chapa.saidas["fita_transversal"].texto_completo() == "3022,00"
    assert not (tmp_path / "configuracao.json").exists()


def test_valor_invalido_avisa_e_nao_salva(janela, tmp_path):
    def zerar_altura(dialogo):
        dialogo.campos["altura_madeira"].setText("0")
        dialogo._salvar()
        assert "Altura da madeira: precisa ser maior que zero" in dialogo.erro.text()
        assert dialogo.result() != QDialog.Accepted
        dialogo.reject()

    usar_dialogo(janela, zerar_altura)
    janela.abrir_editar()
    assert janela.fixos == ValoresFixos()
    assert not (tmp_path / "configuracao.json").exists()


def test_edicao_comeca_com_os_valores_atuais(app, tmp_path):
    atuais = ValoresFixos(densidade_aco=7.9, quantidade_madeiras=3)
    dialogo = DialogoEditar(None, Configuracao(tmp_path), atuais)
    assert dialogo.campos["densidade_aco"].text() == "7,9"
    assert dialogo.campos["quantidade_madeiras"].text() == "3"
    assert dialogo.campos["altura_madeira"].text() == "65"


def test_campo_vazio_ou_com_letra_avisa(app, tmp_path):
    dialogo = DialogoEditar(None, Configuracao(tmp_path), ValoresFixos())
    dialogo.campos["cava_largura"].setText("")
    dialogo.campos["folga_fita"].setText("1o0")
    dialogo._salvar()
    assert "Cava — largura: preencha o valor." in dialogo.erro.text()
    assert "Folga da fita: '1o0' não é um número" in dialogo.erro.text()
