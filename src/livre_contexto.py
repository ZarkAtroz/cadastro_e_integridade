"""
Reconhecedor LLC — parênteses, colchetes e chaves balanceados
Hierarquia de Chomsky: Linguagem Livre de Contexto → PDA

GLC equivalente:
    S → S S | ( S ) | [ S ] | { S } | T | ε
    T → letra | dígito | operador | espaço | T T

Uso:
    python src/livre_contexto.py "((x+y)*z)"
    python src/livre_contexto.py "((a+b)"
    python src/livre_contexto.py "((x+y)*z)" --trace
"""
from __future__ import annotations

import argparse
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from automato import PDA

# ---------------------------------------------------------------------------
# Alfabeto e conjuntos auxiliares
# ---------------------------------------------------------------------------

ABRIDORES: dict[str, str] = {'(': ')', '[': ']', '{': '}'}   # abridor → fechador
FECHADORES: dict[str, str] = {v: k for k, v in ABRIDORES.items()}  # fechador → abridor

NEUTROS: set[str] = (
    set(string.ascii_letters)
    | set(string.digits)
    | set('+-*/')
    | {' '}
)

ALFABETO: set[str] = set(ABRIDORES) | set(FECHADORES) | NEUTROS

# Topos possíveis na pilha: os 3 abridores + fundo
TOPOS: list[str] = list(ABRIDORES.keys()) + ['$']


def build_balanceado_pda() -> PDA:
    """
    Reconhece expressoes com (), [], {} balanceados e aninhados (LLC — Livre de Contexto).

    Constrói o PDA para delimitadores balanceados.

    Estados: q (operacional) + q_f (aceitação).
    ε-transição (q, ε, $) → (q_f, $) garante que só aceita com pilha vazia.

    Convenção da classe PDA: push_string é lida da esquerda pra direita;
    o PRIMEIRO caractere de push_string vira o novo topo da pilha.
    Para empilhar X sobre topo Y mantendo Y: push_string = X + Y.
    Exemplo: empilhar '(' sobre '$' → push_string = '($'.
    """
    delta: dict[tuple[str, str, str], set[tuple[str, str]]] = {}

    # 1. Abridores: empilha o abridor, mantém o topo atual
    #    (q, abridor, topo) → (q, abridor + topo)
    for abridor in ABRIDORES:
        for topo in TOPOS:
            chave = ('q', abridor, topo)
            delta[chave] = {('q', abridor + topo)}

    # 2. Fechadores: pop do abridor correspondente (topo correto apenas)
    #    (q, fechador, abridor_correto) → (q, '')
    #    Cruzados (ex: ')' com topo '[') não existem na delta → rejeição automática
    for fechador, abridor in FECHADORES.items():
        chave = ('q', fechador, abridor)
        delta[chave] = {('q', '')}

    # 3. Neutros: consome símbolo, pilha intacta (re-empilha o topo)
    #    (q, neutro, topo) → (q, topo)
    for neutro in NEUTROS:
        for topo in TOPOS:
            chave = ('q', neutro, topo)
            delta[chave] = {('q', topo)}

    # 4. ε-transição de aceitação: só quando topo é '$' (pilha "vazia")
    #    (q, ε, $) → (q_f, $)
    delta[('q', '', '$')] = {('q_f', '$')}

    return PDA(
        alphabet=ALFABETO,
        states={'q', 'q_f'},
        start='q',
        accept={'q_f'},
        delta=delta,
        bottom='$',
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_MAX_LEN = 10_000


def main() -> None:
    """Ponto de entrada CLI do reconhecedor PDA para delimitadores balanceados."""
    parser = argparse.ArgumentParser(
        description='Reconhecedor PDA -- delimitadores balanceados'
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

    pda = build_balanceado_pda()
    aceito, passos = pda.aceita(args.cadeia)

    if args.trace:
        for linha in pda.trace:
            print(linha)
    else:
        resultado = 'aceita' if aceito else 'rejeita'
        print(f"{resultado} ({passos} passos)")


if __name__ == '__main__':
    main()
