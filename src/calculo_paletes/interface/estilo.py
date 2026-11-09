"""Cores e folha de estilo.

O padrão dos programas da MG é o tema escuro; neste programa o usuário pediu para ver o tema
**claro** (2026-11-09). Os dois ficam aqui: para trocar, mude ``TEMA``.
O significado das cores é o mesmo nos dois: vermelho = erro, amarelo = aviso,
verde = o que está certo (não há botão de ação: as contas se refazem enquanto se digita).
"""

TEMA_ESCURO = {
    "fundo": "#000000",
    "caixa": "#0a0a0a",
    "campo": "#161616",
    "campo_borda": "#3a3a3a",
    "borda": "#e0e0e0",
    "titulo": "#ffffff",
    "texto": "#f0f0f0",
    "texto_campo": "#ffffff",
    "apagado": "#9e9e9e",
    "aba": "#161616",
    "selecao": "#424242",
    "certo": "#43a047",
    "aviso_fundo": "#ffd54f",
    "aviso_texto": "#000000",
    "erro": "#ef5350",
}

TEMA_CLARO = {
    "fundo": "#ffffff",
    "caixa": "#fafafa",
    "campo": "#ffffff",
    "campo_borda": "#9e9e9e",
    "borda": "#424242",
    "titulo": "#000000",
    "texto": "#212121",
    "texto_campo": "#000000",
    "apagado": "#6e6e6e",
    "aba": "#eeeeee",
    "selecao": "#cfd8dc",
    "certo": "#2e7d32",
    "aviso_fundo": "#ffd54f",
    "aviso_texto": "#000000",
    "erro": "#c62828",
}

TEMA = TEMA_CLARO

# O logo original tem letras brancas (somem no fundo branco): no tema claro usa a cópia com as
# letras escuras, gerada na pasta de dados. Sem ela, cai no logo normal.
LOGOS = ["logo_mg_escuro.png", "logo_mg.png"] if TEMA is TEMA_CLARO else ["logo_mg.png"]

_MODELO = """
QWidget {{ font-size: 13pt; color: {texto}; font-family: "Segoe UI"; }}
QMainWindow, #central {{ background: {fundo}; }}
QGroupBox {{ font-size: 15pt; font-weight: bold; background: {caixa};
             border: 1px solid {borda}; border-radius: 6px; margin-top: 12px;
             padding: 14px 10px 8px 10px; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; color: {titulo}; }}
QGroupBox QLabel {{ font-weight: normal; font-size: 16pt; }}
QLineEdit {{ font-size: 18pt; background: {campo}; border: 1px solid {campo_borda};
             border-radius: 4px; padding: 10px; color: {texto_campo};
             selection-background-color: {selecao}; selection-color: {texto_campo}; }}
QLineEdit:focus {{ border: 2px solid {borda}; }}
QToolTip {{ background: {campo}; color: {texto}; border: 1px solid {borda}; }}
#titulo {{ font-size: 22pt; font-weight: bold; letter-spacing: 3px; color: {titulo}; }}
#versao, #dica, #unidade {{ color: {apagado}; }}
#dica {{ font-style: italic; }}
#resultado {{ font-size: 28pt; font-weight: bold; padding: 6px 14px; color: {texto_campo};
              border: 2px solid {campo_borda}; border-radius: 4px; }}
#resultado_grande {{ font-size: 44pt; font-weight: bold; padding: 10px 18px;
                     color: {texto_campo}; border: 2px solid {campo_borda};
                     border-radius: 4px; }}
#resultado[calculado="true"], #resultado_grande[calculado="true"] {{
    border: 2px solid {certo}; }}
#resultado[estouro="true"], #resultado_grande[estouro="true"] {{
    background: {aviso_fundo}; color: {aviso_texto}; border: 2px solid {aviso_fundo}; }}
#erro {{ color: {erro}; }}
#fixo {{ color: {titulo}; font-weight: bold; }}
#rodape QLabel {{ font-size: 14pt; }}
QPushButton {{ background: {campo}; border: 1px solid {borda}; border-radius: 6px;
               padding: 8px 28px; color: {texto}; }}
QPushButton:hover {{ background: {selecao}; }}
QPushButton:disabled {{ color: {apagado}; border: 1px solid {campo_borda}; }}
QDialog {{ background: {fundo}; }}
#botao_menu {{ font-size: 26pt; border: none; background: transparent; padding: 0 6px; }}
#botao_menu:hover {{ background: {aba}; }}
#fundo_menu {{ background: rgba(0, 0, 0, 70); }}
#painel_menu {{ background: {caixa}; border-right: 1px solid {borda}; }}
#titulo_menu {{ font-size: 15pt; font-weight: bold; color: {apagado}; letter-spacing: 2px; }}
#opcao_menu {{ font-size: 16pt; font-weight: bold; text-align: left; padding: 12px 18px; }}
QTabWidget::pane {{ border: 1px solid {borda}; border-radius: 6px; top: -1px; }}
QTabBar::tab {{ background: {aba}; border: 1px solid {campo_borda}; border-bottom: none;
               border-top-left-radius: 6px; border-top-right-radius: 6px;
               padding: 8px 36px; margin-right: 4px; color: {apagado}; }}
QTabBar::tab:selected {{ background: {caixa}; border: 1px solid {borda}; border-bottom: none;
                        color: {titulo}; font-weight: bold; }}
"""


def montar_estilo(tema: dict[str, str]) -> str:
    return _MODELO.format(**tema)


ESTILO = montar_estilo(TEMA)
