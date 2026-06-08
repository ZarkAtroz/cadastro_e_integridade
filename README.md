# Projeto Final — Linguagens Formais

Três reconhecedores implementando a hierarquia de Chomsky **LR ⊊ LLC ⊊ R**,
cada um como simulador explícito de autômato com tabela de transição declarativa.

| Nível | Linguagem | Modelo | Arquivo |
|-------|-----------|--------|---------|
| LR  | CPF no formato `ddd.ddd.ddd-dd` | DFA | `src/regular.py` |
| LLC | `()`, `[]`, `{}` balanceados e aninhados | PDA | `src/livre_contexto.py` |
| R   | `{w#w \| w ∈ {0,1}*}` | Máquina de Turing | `src/recursiva.py` |

---

## Bateria completa em um comando

```
python src/testes.py
```

Saída esperada: `TOTAL: 34/34  [OK] TODOS PASSARAM`

Para ver só os resumos sem tabelas:

```
python src/testes.py --quiet
```

Para tabelas sem passo a passo:

```
python src/testes.py --no-trace
```

---

## Reconhecedores standalone

Cada reconhecedor aceita uma cadeia como argumento e imprime `aceita|rejeita (N passos)`.
A flag `--trace` imprime o passo a passo do autômato.

```bash
# DFA — CPF
python src/regular.py "123.456.789-00"
python src/regular.py "12.345.678-90"
python src/regular.py "123.456.789-00" --trace

# PDA — parênteses
python src/livre_contexto.py "({a+b})"
python src/livre_contexto.py "((a+b)"
python src/livre_contexto.py "({a+b})" --trace

# MT — w#w
python src/recursiva.py "101#101"
python src/recursiva.py "0#1"
python src/recursiva.py "101#101" --trace
```

---

## Dependências

Python 3.11 ou superior.

```
pip install -r requirements.txt
```

**Nota sobre Graphviz:** o pacote Python `graphviz` (listado em `requirements.txt`) é
apenas um binding. Para renderizar os arquivos `.dot` em `.svg` é necessário o binário
do sistema:

```bash
# Ubuntu / Debian
apt install graphviz

# macOS
brew install graphviz

# Windows
winget install graphviz
```

Os arquivos `.dot` estão versionados em `diagramas/`. Os `.svg` podem ser regerados com:

```
dot -Tsvg diagramas/dfa_regular.dot        -o diagramas/dfa_regular.svg
dot -Tsvg diagramas/pda_livre_contexto.dot -o diagramas/pda_livre_contexto.svg
dot -Tsvg diagramas/mt_recursiva.dot       -o diagramas/mt_recursiva.svg
```

---

## Testes pytest

```
pytest tests_pytest/ -v
```

Saída esperada: `92 passed`.

---

## Estrutura do repositório

```
projeto/
├── README.md                        # este arquivo
├── requirements.txt                 # dependências Python
├── .gitignore
├── src/
│   ├── regular.py                   # DFA do CPF, executável standalone
│   ├── livre_contexto.py            # PDA de parênteses, executável standalone
│   ├── recursiva.py                 # MT w#w, executável standalone
│   ├── testes.py                    # bateria unificada dos 3 reconhecedores
│   ├── bonus_dfa_vs_re.py           # bonus 1: comparacao DFA x re
│   ├── app_streamlit.py             # bonus 2: interface web Streamlit
│   ├── bonus_grafico_passos.py      # bonus 3: grafico de complexidade
│   └── automato/
│       ├── __init__.py              # exporta DFA, PDA, MT, load_test_cases
│       ├── dfa.py                   # classe base DFA
│       ├── pda.py                   # classe base PDA (BFS não-determinístico)
│       ├── mt.py                    # classe base MT (fita infinita)
│       └── io.py                    # parser compartilhado de arquivos .txt
├── testes/
│   ├── testes_regular.txt           # 3 aceitas + 6 rejeitadas (CPF)
│   ├── testes_livre_contexto.txt    # 6 aceitas + 6 rejeitadas (parênteses)
│   └── testes_recursiva.txt         # 6 aceitas + 7 rejeitadas (w#w)
├── tests_pytest/
│   ├── test_dfa.py                  # smoke tests da classe DFA
│   ├── test_pda.py                  # smoke tests da classe PDA
│   ├── test_mt.py                   # smoke tests da classe MT
│   ├── test_regular.py              # testes do DFA CPF
│   ├── test_livre_contexto.py       # testes do PDA parênteses
│   └── test_recursiva.py            # testes da MT w#w
├── diagramas/
│   ├── dfa_regular.dot              # diagrama DFA (rankdir=LR)
│   ├── pda_livre_contexto.dot       # diagrama PDA (2 estados)
│   └── mt_recursiva.dot             # diagrama MT (12 estados)
└── relatorio/
    ├── relatorio.pdf                # (a entregar)
    └── grafico_passos.png           # gerado por bonus_grafico_passos.py
```

---

## Bônus

### Bônus 1 — Comparação DFA × `re`

Demonstra que o DFA manual e o `re.fullmatch` reconhecem a mesma linguagem regular,
concordando em 100% dos casos de teste.

```
python src/bonus_dfa_vs_re.py
```

### Bônus 2 — Interface Streamlit

Interface web com 3 abas (uma por linguagem), exemplos clicáveis, resultado destacado
e trace completo opcional.

```
streamlit run src/app_streamlit.py
```

Acesse `http://localhost:8501` após iniciar.

### Bônus 3 — Gráfico de crescimento de passos

Gera `relatorio/grafico_passos.png` com os 3 subplots (DFA, PDA, MT) mostrando
crescimento medido vs curva teórica. Imprime os valores numéricos no stdout.

```
python src/bonus_grafico_passos.py
```

Complexidades observadas: DFA O(n) com a=1.00, PDA O(n) com a=2.00 (passos=2N+1),
MT O(n²) com a=2.00.

---

## Decisões de design

- **Cadeia vazia aceita em LLC:** a gramática define `S → ε`, então `""` é uma
  expressão válida sem delimitadores. Documentado como critério puramente sintático.

- **MT com 12 estados (não 11):** o estado `q_return` foi dividido em `q_return`
  (lado direito do `#`, passa por X/Y marcados) e `q_return_l` (lado esquerdo,
  passa por 0/1 não marcados). Necessário para distinguir o lado da fita durante
  o retorno — um estado único parava no primeiro marcador encontrado, que podia
  ser do lado errado.

- **DFA do CPF valida apenas o formato textual** (`ddd.ddd.ddd-dd`), sem verificar
  os dígitos verificadores. Validar os dígitos exigiria aritmética, o que tornaria
  o problema não-regular.
