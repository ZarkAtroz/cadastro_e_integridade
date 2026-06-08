"""
Reconhecedor R — L = {w#w | w ∈ {0,1}*}
Hierarquia de Chomsky: Linguagem Recursiva → Máquina de Turing

Algoritmo: marcação por correspondência par-a-par.
  1. Marca o 1º símbolo não-marcado à esquerda (0→X, 1→Y).
  2. Anda direita, passa o #, acha o 1º não-marcado à direita.
  3. Compara. Diferente → q_reject.
  4. Marca à direita também, volta L até o último marcador.
  5. Repete. Quando # é encontrado à esquerda, toda a esquerda está marcada;
     verifica que à direita só restam X/Y (sem 0/1 sobrando).
  Caso especial: "#" → w=ε, aceita diretamente se direita for branco.

Uso:
    python src/recursiva.py "101#101"
    python src/recursiva.py "0#1"
    python src/recursiva.py "101#101" --trace
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from automato import MT

# ---------------------------------------------------------------------------
# Alfabetos
# ---------------------------------------------------------------------------

INPUT_ALPHABET: set[str] = {'0', '1', '#'}
TAPE_ALPHABET:  set[str] = {'0', '1', '#', 'X', 'Y', '_'}

# ---------------------------------------------------------------------------
# Tabela de transições (dict-of-dicts, achata para MT.delta)
# ---------------------------------------------------------------------------
# Formato interno: {estado: {símbolo_lido: (próximo_estado, escrito, mov)}}
# Γ = {0, 1, #, X, Y, _}

_TRANSITIONS: dict[str, dict[str, tuple[str, str, str]]] = {

    # ------------------------------------------------------------------ q_start
    # Lê o 1º símbolo da fita.
    'q_start': {
        '0': ('q_seek_hash_a_0', 'X', 'R'),
        '1': ('q_seek_hash_a_1', 'Y', 'R'),
        '#': ('q_verify_right_blank', '#', 'R'),  # w = ε
        '_': ('q_reject',  '_', 'S'),
        'X': ('q_reject',  'X', 'S'),
        'Y': ('q_reject',  'Y', 'S'),
    },

    # --------------------------------------------------- q_seek_hash_a_0 / _1
    # Anda R passando por 0,1 até encontrar o #.
    'q_seek_hash_a_0': {
        '0': ('q_seek_hash_a_0', '0', 'R'),
        '1': ('q_seek_hash_a_0', '1', 'R'),
        '#': ('q_find_0_right',  '#', 'R'),
        'X': ('q_reject', 'X', 'S'),
        'Y': ('q_reject', 'Y', 'S'),
        '_': ('q_reject', '_', 'S'),
    },
    'q_seek_hash_a_1': {
        '0': ('q_seek_hash_a_1', '0', 'R'),
        '1': ('q_seek_hash_a_1', '1', 'R'),
        '#': ('q_find_1_right',  '#', 'R'),
        'X': ('q_reject', 'X', 'S'),
        'Y': ('q_reject', 'Y', 'S'),
        '_': ('q_reject', '_', 'S'),
    },

    # ------------------------------------------------- q_find_0_right / _1
    # Acha o 1º símbolo não-marcado à direita do #; compara.
    'q_find_0_right': {
        'X': ('q_find_0_right', 'X', 'R'),   # pula marcados
        'Y': ('q_find_0_right', 'Y', 'R'),
        '0': ('q_return',       'X', 'L'),   # match: marca, volta
        '1': ('q_reject',       '1', 'S'),   # mismatch
        '_': ('q_reject',       '_', 'S'),   # direita menor que esquerda
        '#': ('q_reject',       '#', 'S'),   # múltiplos #
    },
    'q_find_1_right': {
        'X': ('q_find_1_right', 'X', 'R'),
        'Y': ('q_find_1_right', 'Y', 'R'),
        '1': ('q_return',       'Y', 'L'),   # match
        '0': ('q_reject',       '0', 'S'),   # mismatch
        '_': ('q_reject',       '_', 'S'),
        '#': ('q_reject',       '#', 'S'),
    },

    # ------------------------------------------------------------ q_return
    # Fase 1 do retorno: ainda no lado direito do #, passa por X/Y marcados.
    # Ao cruzar o # entra em q_return_l.
    'q_return': {
        'X': ('q_return',   'X', 'L'),   # passa marcadores do lado direito
        'Y': ('q_return',   'Y', 'L'),
        '#': ('q_return_l', '#', 'L'),   # cruzou o #; agora no lado esquerdo
        '0': ('q_reject',   '0', 'S'),   # símbolo bruto na direita = erro
        '1': ('q_reject',   '1', 'S'),
        '_': ('q_reject',   '_', 'S'),
    },

    # ---------------------------------------------------------- q_return_l
    # Fase 2 do retorno: lado esquerdo do #, passa por 0/1 não-marcados.
    # Para no primeiro X/Y encontrado (último marcador esquerdo).
    'q_return_l': {
        '0': ('q_return_l',   '0', 'L'),   # passa símbolos ainda não marcados
        '1': ('q_return_l',   '1', 'L'),
        'X': ('q_next_round', 'X', 'R'),   # chegou ao último marcador esquerdo
        'Y': ('q_next_round', 'Y', 'R'),
        '_': ('q_next_round', '_', 'R'),   # início da fita (sem marcadores à esq.)
        '#': ('q_reject',     '#', 'S'),   # nunca deve ocorrer
    },

    # --------------------------------------------------------- q_next_round
    # Lê o próximo símbolo não-marcado à esquerda do #.
    'q_next_round': {
        '0': ('q_seek_hash_a_0', 'X', 'R'),
        '1': ('q_seek_hash_a_1', 'Y', 'R'),
        '#': ('q_verify_right_all_marked', '#', 'R'),  # esquerda toda marcada
        'X': ('q_reject', 'X', 'S'),
        'Y': ('q_reject', 'Y', 'S'),
        '_': ('q_reject', '_', 'S'),
    },

    # ------------------------------------------------ q_verify_right_blank
    # w = ε: após #, deve vir imediatamente branco.
    'q_verify_right_blank': {
        '_': ('q_accept', '_', 'S'),
        '0': ('q_reject', '0', 'S'),
        '1': ('q_reject', '1', 'S'),
        '#': ('q_reject', '#', 'S'),
        'X': ('q_reject', 'X', 'S'),
        'Y': ('q_reject', 'Y', 'S'),
    },

    # ----------------------------------------- q_verify_right_all_marked
    # Toda a esquerda foi marcada; verifica que direita só tem X/Y (sem 0/1).
    'q_verify_right_all_marked': {
        'X': ('q_verify_right_all_marked', 'X', 'R'),
        'Y': ('q_verify_right_all_marked', 'Y', 'R'),
        '_': ('q_accept', '_', 'S'),
        '0': ('q_reject', '0', 'S'),   # direita maior que esquerda
        '1': ('q_reject', '1', 'S'),
        '#': ('q_reject', '#', 'S'),
    },
}


def build_ww_mt() -> MT:
    """
    Reconhece L = {w#w | w em {0,1}*} (R — Linguagem Recursiva).

    Constrói a MT de fita unica com 12 estados operacionais.
    """
    estados: set[str] = set(_TRANSITIONS.keys()) | {'q_accept', 'q_reject'}

    # Achata dict-of-dicts → dict plano esperado por MT
    delta: dict[tuple[str, str], tuple[str, str, str]] = {}
    for estado, transicoes in _TRANSITIONS.items():
        for lido, acao in transicoes.items():
            delta[(estado, lido)] = acao

    return MT(
        states=estados,
        alphabet=TAPE_ALPHABET,
        input_alphabet=INPUT_ALPHABET,
        start='q_start',
        halt_accept='q_accept',
        halt_reject='q_reject',
        delta=delta,
        blank='_',
        max_steps=100_000,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _formata_fita(fita: list[str], cabeca: int) -> str:
    """Retorna a fita como string com '>' marcando a posição da cabeça."""
    partes = []
    for i, c in enumerate(fita):
        partes.append(f">{c}" if i == cabeca else c)
    return ''.join(partes)


_MAX_LEN = 10_000


def main() -> None:
    """Ponto de entrada CLI do reconhecedor MT para L = {w#w | w em {0,1}*}."""
    parser = argparse.ArgumentParser(
        description='Reconhecedor MT -- L = {w#w | w em {0,1}*}'
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

    mt = build_ww_mt()
    aceito, passos = mt.aceita(args.cadeia)

    if args.trace:
        for linha in mt.trace:
            print(linha)
    else:
        resultado = 'aceita' if aceito else 'rejeita'
        print(f"{resultado} ({passos} passos)")


if __name__ == '__main__':
    main()
