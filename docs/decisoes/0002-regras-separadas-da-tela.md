# 0002 — Fórmulas puras, separadas da tela, conferidas com a planilha

- **Status:** aceita
- **Data:** 2026-11-09

## Contexto
A planilha tinha versões diferentes da mesma conta (ex.: duas fórmulas de fita) e o resultado
"quebrado" de blanks por pilha (163,2 blanks). Era preciso saber qual conta é a certa e garantir
que ela não mude sem querer.

## Decisão
- As fórmulas ficam em `regras/` como **funções puras** (sem Qt), testadas sozinhas com pytest.
- Valem as **células verdes** da planilha (as que a engenharia usa); as outras não entram.
- **Blanks por pilha arredondados para cima** e a altura da pilha usa esse número já arredondado
  (decisão do usuário: não existe meio blank).
- Chapa e trapézio usam **a mesma conta**; só muda a área do blank.
- Testes com números **fictícios** vão para o GitHub; testes com os números da planilha real ficam
  só no PC (`dados/testes/`), conferindo os pesos com as células do Excel.

## Consequências
- ✅ Cada linha de fórmula corresponde a uma linha da regra no `CLAUDE.md`; fácil de conferir.
- ✅ A tela não tem nenhuma conta: trocar a interface não mexe nas regras.
- ⚠️ Os resultados de altura, fita e plástico ficam um pouco diferentes da planilha antiga (de
  propósito, por causa do arredondamento dos blanks).
