# 0003 — Valores fixos editáveis, gravados num arquivo JSON na rede

- **Status:** aceita
- **Data:** 2026-11-09

## Contexto
As contas usam valores de referência (densidade do aço e da madeira, altura e seção da madeira,
cava, folga da fita) que ficavam escondidos dentro das fórmulas da planilha. A engenharia quer
vê-los na tela e poder mudá-los, e a mudança deve valer para todos.

## Decisão
- Os valores ficam num só lugar (`ValoresFixos`), **sempre visíveis** em cada aba.
- Menu **☰ → EDITAR** abre os valores com **Salvar** e **Cancelar**; as três abas refazem as
  contas na hora.
- Gravação em `dados/configuracao.json` na pasta da rede, por uma classe repositório
  (`Configuracao`), com gravação segura (arquivo temporário trocado de uma vez).
- **Sem senha:** foi testada a pedido do usuário e retirada por decisão dele.

## Alternativas consideradas
- **SQLite:** exagero para nove números.
- **Valores só no código:** mudar exigiria gerar o programa de novo.

## Consequências
- ✅ Todo mundo sabe com quais valores a conta foi feita; mudar não exige programador.
- ✅ Arquivo estragado vira aviso e o programa abre com os valores da planilha.
- ⚠️ Qualquer pessoa pode mudar os valores (não há senha nem histórico de quem mudou).
