"""
Bonus 3 - Grafico de crescimento de passos por tamanho da entrada.

Gera 3 subplots (DFA, PDA, MT) com dados medidos e curvas teoricas.
Salva em relatorio/grafico_passos.png (300 DPI).

Uso:
    python src/bonus_grafico_passos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import matplotlib
matplotlib.use("Agg")           # backend sem GUI - funciona em qualquer ambiente
import matplotlib.pyplot as plt

from regular import build_cpf_dfa
from livre_contexto import build_balanceado_pda
from recursiva import build_ww_mt

# ---------------------------------------------------------------------------
# Coleta de dados
# ---------------------------------------------------------------------------

def medir_dfa(ns: list[int]) -> list[int]:
    """
    Cadeias formadas so de digitos (sem pontuacao) -> vai ao trap no 1o passo
    e absorve linearmente os restantes. Complexidade O(n).
    """
    resultados = []
    for n in ns:
        cadeia = '1' * n
        dfa = build_cpf_dfa()
        _, passos = dfa.aceita(cadeia)
        resultados.append(passos)
    return resultados


def medir_pda(ns: list[int]) -> list[int]:
    """
    Cadeias '(' * N + ')' * N (tamanho 2N). Complexidade O(n).
    """
    resultados = []
    for n in ns:
        cadeia = '(' * n + ')' * n
        pda = build_balanceado_pda()
        _, passos = pda.aceita(cadeia)
        resultados.append(passos)
    return resultados


def medir_mt(ns: list[int]) -> list[int]:
    """
    Cadeias '0' * N + '#' + '0' * N (tamanho 2N+1). Complexidade O(n^2).
    """
    resultados = []
    for n in ns:
        cadeia = '0' * n + '#' + '0' * n
        mt = build_ww_mt()
        _, passos = mt.aceita(cadeia)
        resultados.append(passos)
    return resultados


# ---------------------------------------------------------------------------
# Impressao de tabela no stdout
# ---------------------------------------------------------------------------

def imprimir_tabela(modelo: str, ns: list[int], passos: list[int],
                    ajuste: str | None = None) -> None:
    print(f"{modelo}:")
    for n, p in zip(ns, passos):
        print(f"  N={n:<6}  passos={p}")
    if ajuste:
        print(f"  {ajuste}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Tamanhos de entrada por modelo
    ns_dfa = [1, 5, 10, 50, 100, 500, 1000]
    ns_pda = [1, 5, 10, 50, 100, 500]
    ns_mt  = [1, 2, 5, 10, 20, 50]

    # Medicoes
    passos_dfa = medir_dfa(ns_dfa)
    passos_pda = medir_pda(ns_pda)
    passos_mt  = medir_mt(ns_mt)

    # Ajuste polinomial grau 2 para MT (a*N^2 + b*N + c)
    coefs = np.polyfit(ns_mt, passos_mt, 2)
    a_mt  = coefs[0]
    ajuste_str = f"Ajuste polinomial: passos ~~ a*N^2 com a = {a_mt:.2f}"

    # Impressao no stdout
    imprimir_tabela("DFA", ns_dfa, passos_dfa)
    imprimir_tabela("PDA", ns_pda, passos_pda)
    imprimir_tabela("MT",  ns_mt,  passos_mt, ajuste=ajuste_str)

    # ---------------------------------------------------------------------------
    # Figura
    # ---------------------------------------------------------------------------
    fig, axes = plt.subplots(3, 1, figsize=(8, 12))
    fig.suptitle("Crescimento de passos por modelo de automato", fontsize=14)

    # --- DFA ---
    ax = axes[0]
    teorico_dfa = [n for n in ns_dfa]
    ax.plot(ns_dfa, passos_dfa,  'o-',  label="medido",   color="steelblue")
    ax.plot(ns_dfa, teorico_dfa, '--',  label="teorico O(n)", color="tomato")
    ax.set_title("DFA - CPF (cadeias invalidas)  |  complexidade: O(n)")
    ax.set_xlabel("Tamanho da entrada (n)")
    ax.set_ylabel("Passos")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # --- PDA ---
    ax = axes[1]
    tamanhos_pda = [2 * n for n in ns_pda]   # cadeia tem tamanho 2N
    teorico_pda  = [p + 1 for p in tamanhos_pda]  # 2N passos + 1 epsilon
    ax.plot(tamanhos_pda, passos_pda,  'o-',  label="medido",       color="steelblue")
    ax.plot(tamanhos_pda, teorico_pda, '--',  label="teorico O(n)", color="tomato")
    ax.set_title("PDA - Parenteses balanceados  |  complexidade: O(n)")
    ax.set_xlabel("Tamanho da entrada (n = 2N)")
    ax.set_ylabel("Passos")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # --- MT ---
    ax = axes[2]
    tamanhos_mt = [2 * n + 1 for n in ns_mt]  # cadeia tem tamanho 2N+1
    teorico_mt  = [a_mt * n**2 for n in ns_mt]
    ax.plot(ns_mt, passos_mt,  'o-',  label="medido",          color="steelblue")
    ax.plot(ns_mt, teorico_mt, '--',  label=f"teorico {a_mt:.2f}*N^2", color="tomato")
    ax.set_title("MT - w#w  |  complexidade: O(n^2)")
    ax.set_xlabel("Tamanho de w (N, cadeia = 2N+1)")
    ax.set_ylabel("Passos")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Salva
    destino = Path(__file__).parent.parent / "relatorio" / "grafico_passos.png"
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=300)
    plt.close(fig)

    print(f"Grafico salvo em {destino}")
    sys.exit(0)


if __name__ == "__main__":
    main()
