"""
Reconhecedor LR — CPF no formato ddd.ddd.ddd-dd
Hierarquia de Chomsky: Linguagem Regular → DFA

Uso:
    python src/regular.py "123.456.789-00"
    python src/regular.py "123.456.789-00" --trace
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from automato import DFA

# ---------------------------------------------------------------------------
# Alfabeto e padrão posicional
# ---------------------------------------------------------------------------

DIGITOS: set[str] = set('0123456789')
ALFABETO: set[str] = DIGITOS | {'.', '-'}

# Padrão: 'D' = qualquer dígito, '.' = ponto literal, '-' = hífen literal
# Posições: 0  1  2  3  4  5  6  7  8  9  10  11  12  13
PADRAO = ['D','D','D','.','D','D','D','.','D','D','D', '-','D', 'D']

TRAP = 'q_trap'


def build_cpf_dfa() -> DFA:
    """
    Reconhece CPF no formato textual ddd.ddd.ddd-dd (LR — Linguagem Regular).

    Constrói o DFA programaticamente a partir de PADRAO.

    Estados: q0 (início) … q14 (único final) + q_trap (sink).
    Nenhuma entrada de transição escrita manualmente.
    """
    n = len(PADRAO)                        # 14 posições
    estados: set[str] = {f'q{i}' for i in range(n + 1)} | {TRAP}
    inicio = 'q0'
    finais = {'q14'}
    delta: dict[tuple[str, str], str] = {}

    for i, esperado in enumerate(PADRAO):
        estado_atual = f'q{i}'
        proximo = f'q{i + 1}'

        # Símbolos que avançam o estado
        if esperado == 'D':
            simbolos_ok = DIGITOS
        else:
            simbolos_ok = {esperado}        # '.' ou '-'

        for s in ALFABETO:
            delta[(estado_atual, s)] = proximo if s in simbolos_ok else TRAP

    # q14 (final): qualquer símbolo adicional → trap (excesso de caracteres)
    for s in ALFABETO:
        delta[('q14', s)] = TRAP

    # q_trap: sink absorvente para todo o alfabeto
    for s in ALFABETO:
        delta[(TRAP, s)] = TRAP

    return DFA(
        alphabet=ALFABETO,
        states=estados,
        start=inicio,
        accept=finais,
        delta=delta,
        trap=TRAP,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_MAX_LEN = 10_000


def main() -> None:
    """Ponto de entrada CLI do reconhecedor DFA para CPF."""
    parser = argparse.ArgumentParser(
        description='Reconhecedor DFA -- CPF (formato ddd.ddd.ddd-dd)'
    )
    parser.add_argument('cadeia', help='Cadeia a ser reconhecida')
    parser.add_argument(
        '--trace', action='store_true',
        help='Imprime passo a passo do automato'
    )
    args = parser.parse_args()

    if len(args.cadeia) > _MAX_LEN:
        print(f"Erro: cadeia muito longa ({len(args.cadeia)} chars, max {_MAX_LEN}).",
              file=sys.stderr)
        sys.exit(2)
    if args.cadeia and not args.cadeia.isprintable():
        print("Erro: cadeia contem caracteres nao-imprimiveis.", file=sys.stderr)
        sys.exit(2)

    dfa = build_cpf_dfa()
    aceito, passos = dfa.aceita(args.cadeia)

    if args.trace:
        for linha in dfa.trace:
            print(linha)
    else:
        resultado = 'aceita' if aceito else 'rejeita'
        print(f"{resultado} ({passos} passos)")


if __name__ == '__main__':
    main()
