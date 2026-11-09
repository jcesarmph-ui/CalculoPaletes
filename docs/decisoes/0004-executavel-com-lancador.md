# 0004 — Executável com lançador e pasta na rede

- **Status:** aceita
- **Data:** 2026-11-09

## Contexto
O programa fica numa pasta comum da rede, sem servidor. Abrir um programa PySide6 direto da rede
é lento, porque o Windows puxa dezenas de MB a cada abertura.

## Decisão
- Igual aos outros programas: o `.exe` da rede é um **lançador** pequeno (sem Qt) que copia o
  programa para o PC **uma vez por versão** e abre a cópia; a pasta `dados` continua só na rede.
- Cópia feita numa pasta temporária e renomeada no fim: cópia interrompida nunca é usada.
- As pastas `_internal`, `programa` e `dados` ficam ocultas: na rede só se vê o `.exe`.
- Os scripts de gerar o `.exe` ficam **fora do GitHub público**.

## Consequências
- ✅ Abre em 1–2 s depois da primeira vez; atualizar = trocar a pasta `programa`.
- ✅ Valores fixos iguais para todos (lidos da rede).
- ⚠️ Na primeira abertura em cada PC (e a cada versão) aparece "Preparando…" por alguns segundos.
