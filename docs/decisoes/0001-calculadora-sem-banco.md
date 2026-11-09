# 0001 — Só calculadora: sem banco, sem histórico e sem trava de edição

- **Status:** aceita
- **Data:** 2026-11-09

## Contexto
A engenharia fazia as contas do palete (blanks por pilha, alturas, fita, plástico e peso da
madeira) numa planilha com campos de entrada e de resultado espalhados, fórmulas misturadas e
células de teste. Os outros programas internos guardam histórico em SQLite na rede, com Lixeira e
trava de edição para duas pessoas não gravarem ao mesmo tempo.

## Decisão
- O programa é **só uma calculadora**: as contas se refazem a cada tecla, sem botão CALCULAR.
- **Sem banco, sem histórico, sem Lixeira e sem trava de edição** (decisão do usuário).
- A única coisa gravada são os valores fixos do menu EDITAR (ver [0003](0003-valores-fixos-em-json.md)).

## Alternativas consideradas
- **Guardar cada cálculo (SQLite + Lixeira + trava):** útil para consultar depois, mas o usuário
  não precisa disso hoje; traria complexidade (backup, trava, banco na rede) sem ganho.

## Consequências
- ✅ Programa simples, rápido (recálculo em menos de 1 ms por tecla) e sem risco de banco travado.
- ✅ Sem trava: várias pessoas usam ao mesmo tempo sem atrapalhar umas às outras.
- ⚠️ Se um dia quiserem guardar os cálculos, volta o padrão dos outros programas (banco + trava).
