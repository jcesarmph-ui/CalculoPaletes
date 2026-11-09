# CalculoPaletes — regras do projeto

Calculadora desktop da **engenharia** para definir o palete de chapas e trapézios (pilhas, alturas,
fita e plástico) e o peso do palete de madeira. Substitui a planilha
`dados/Cálculo de Palete e Chapa - copia.xlsx` (dado da empresa, fora do Git).

O padrão geral (idioma, Git, arquitetura, visual, versão) está no `CLAUDE.md` do usuário; aqui fica
só o que é deste programa.

## O que o programa é (e não é)
- **Só calculadora**: as contas se refazem enquanto o usuário digita. **Sem banco, sem histórico,
  sem Lixeira e sem trava de edição** (decisão do usuário, 2026-11-09).
- A única coisa gravada são os **valores fixos** alterados no menu ☰ → **EDITAR**; ficam valendo
  para sempre (até editar de novo) em `dados/configuracao.json` (classe `Configuracao`, em
  `armazenamento/`), para todos que usam o programa.
- **EDITAR sem senha** (decisão do usuário, 2026-11-09: a senha foi feita só para ele ver
  funcionando e depois retirada). Tem **Salvar** e **Cancelar**; sem botão "voltar aos valores da
  planilha". Folga da fita e cava aceitam zero ("não tem"); os outros valores precisam ser > 0 e
  as madeiras empilhadas, inteiro.
- O ☰ fica à esquerda do logo (28 px de espaço); o menu abre por cima da tela, pela esquerda, e
  fecha clicando fora, no ☰ ou com Esc.
- Mostrar **só** as saídas listadas abaixo. Fora do programa (até o usuário pedir): custo em R$,
  escolha da bobina de plástico 1600/2200, abas ROLO, PPAP e RNC da planilha.

## Visual (diferenças do padrão geral)
- **Tema claro (branco)**, pedido do usuário em 2026-11-09 — exceção ao tema escuro dos outros
  programas. Os dois temas ficam em `interface/estilo.py` (`TEMA`); o significado das cores é o
  mesmo (verde = certo, vermelho = erro, amarelo = aviso).
- No tema claro o logo usa `dados/logo_mg_escuro.png` (cópia do logo com as letras escurecidas
  da coluna 330 em diante; o símbolo fica igual). Sem ela, usa o `logo_mg.png`.
- **Nenhum número mexe na tela** (teste do usuário com número "infinito"): campos com no máximo
  12 caracteres; caixas de resultado com largura vinda da tela (`RotuloResultado`) — se o número
  não couber, mostra "grande demais" em amarelo, com o número inteiro na dica do mouse.
- A janela tem que caber em 1920 × 1000 (tela do usuário: 1032 px livres) — há teste para isso.
- Sem botão CALCULAR: as contas se refazem a cada tecla.

## Telas (abas CHAPA | TRAPÉZIO | PESO DO PALETE)
| Tela | Entradas | Saídas |
|---|---|---|
| Chapa | espessura, largura, comprimento (mm); qtd a produzir (kg); qtd de pilhas; largura e comprimento do palete (mm) | blanks por pilha, altura da pilha, altura total, fita transversal, fita longitudinal, largura e comprimento do plástico |
| Trapézio | igual à chapa, com base menor, base maior e altura no lugar de largura × comprimento | as mesmas da chapa |
| Peso do palete | até 4 linhas livres de medida (mm) × quantidade (usa só as preenchidas) | peso do palete (kg) |

## Fórmulas (as células verdes da planilha são as certas)
- Peso do blank (kg) = espessura × área × densidade do aço
  - chapa: área = largura × comprimento; trapézio: área = (base menor + base maior) ÷ 2 × altura
- Blanks por pilha = **arredondar para cima**(kg a produzir ÷ peso do blank ÷ qtd de pilhas)
- Altura da pilha = blanks por pilha (**o número já arredondado**) × espessura
- Altura do palete = altura da madeira × qtd de madeiras (65 × 2 = 130)
- Altura total = altura da pilha + altura do palete
- Fita transversal = (altura **total** + largura do palete) × 2 + folga da fita
- Fita longitudinal = (altura **da pilha** + comprimento do palete) × 2 + folga da fita
- Largura do plástico = largura do palete + altura da pilha
- Comprimento do plástico = comprimento do palete × 2 + altura da pilha × 2 (**exato**, sem arredondar)
- Peso do palete (kg) = Σ (seção da madeira − cava) × medida × quantidade × densidade da madeira
  - só madeira 65×65 com cava 10×30 (sem "sem cava" e sem "madeira de 90")

## Valores fixos (aparecem na tela e são editáveis no EDITAR)
| Valor | Padrão |
|---|---|
| Densidade do aço | 7,85 g/cm³ (= 7,85 / 1.000.000 kg/mm³) |
| Densidade da madeira | 0,6 g/cm³ (= 0,6 / 1.000.000 kg/mm³) |
| Altura da madeira | 65 mm |
| Quantidade de madeiras (empilhadas) | 2 |
| Folga da fita | 100 mm |
| Seção da madeira | 65 × 65 mm |
| Cava | 10 × 30 mm |

## Exemplo conferido (números fictícios)
Chapa 1,50 × 1200 × 2000 mm, 3000 kg, 2 pilhas, palete 1250 × 2050 mm →
peso do blank 28,26 kg; 53,08 → **54** blanks por pilha; pilha 81 mm; total 211 mm;
fita transv. 3022 mm; fita long. 4362 mm; plástico 1331 × 4262 mm.

**Dados reais nunca entram no Git** (repositório público): testes versionados usam números
fictícios; testes com os números da planilha ficam em `dados/testes/` (só locais).

## Comandos
- Testes: `.venv/Scripts/python -m pytest`
- Estilo: `.venv/Scripts/python -m ruff check .`
