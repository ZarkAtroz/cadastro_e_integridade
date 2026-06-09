"""
Bonus 1 - Comparacao DFA x re para CPF.

O reconhecedor principal LR continua sendo o DFA manual (regular.py).
Este arquivo demonstra que ambos reconhecem a mesma linguagem regular,
usando as 9 cadeias de testes/testes_regular.txt como corpus.

Uso:
    python src/bonus_dfa_vs_re.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from automato import load_test_cases
from regular import build_cpf_dfa

# Reconhecedor via re (comparacao apenas - NAO e o reconhecedor principal)

_PADRAO_RE = re.compile(r'\d{3}\.\d{3}\.\d{3}-\d{2}')


def validar_cpf_re(s: str) -> bool:
    """Valida formato CPF usando re.fullmatch. Usado apenas para comparacao."""
    return bool(_PADRAO_RE.fullmatch(s))



_BASE = Path(__file__).parent.parent
_TXT  = _BASE / "testes" / "testes_regular.txt"

COL_C = 24
COL_R = 6


def comparar() -> int:
    """
    Compara DFA manual com re sobre todas as cadeias de testes_regular.txt.
    Retorna o numero de divergencias encontradas.
    """
    casos = load_test_cases(_TXT)

    cab_c = "Cadeia".ljust(COL_C)
    print(f"  {cab_c}  {'DFA':<{COL_R}}  {'re':<{COL_R}}  Concordam?")
    print(f"  {'-' * (COL_C + COL_R * 2 + 16)}")

    divergencias = 0
    for cadeia, _ in casos:
        dfa        = build_cpf_dfa()
        dfa_ok, _  = dfa.aceita(cadeia)
        re_ok      = validar_cpf_re(cadeia)

        dfa_r   = "A" if dfa_ok else "R"
        re_r    = "A" if re_ok  else "R"
        concord = "sim" if dfa_ok == re_ok else "NAO <<<"

        if dfa_ok != re_ok:
            divergencias += 1

        c_repr = repr(cadeia).ljust(COL_C)
        print(f"  {c_repr}  {dfa_r:<{COL_R}}  {re_r:<{COL_R}}  {concord}")

    print()
    total = len(casos)
    concordam = total - divergencias
    print(f"  Conclusao: DFA e re concordam em {concordam}/{total} casos.")
    if divergencias == 0:
        print("  Mesma linguagem regular, dois formalismos distintos.")
    else:
        print(f"  ATENCAO: {divergencias} divergencia(s) detectada(s) - revisar DFA ou padrao re.")

    return divergencias


def main() -> None:
    """Executa a comparacao DFA x re e sai com codigo 0 se concordam, 1 se divergem."""
    divergencias = comparar()
    sys.exit(0 if divergencias == 0 else 1)


if __name__ == "__main__":
    main()
