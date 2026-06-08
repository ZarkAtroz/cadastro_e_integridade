"""
Smoke test DFA: reconhece (ab)* — cadeia de comprimento par formada por 'a' seguido de 'b'.
Aceita: "", "ab", "abab"
Rejeita: "a", "ba", "aba", "b"
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from automato import DFA


@pytest.fixture
def dfa_ab_star():
    # L = (ab)*
    # q0: início/par aceito | q1: leu 'a', esperando 'b' | qERRO: rejeição
    return DFA(
        alphabet={'a', 'b'},
        states={'q0', 'q1', 'qERRO'},
        start='q0',
        accept={'q0'},
        delta={
            ('q0', 'a'): 'q1',
            ('q0', 'b'): 'qERRO',
            ('q1', 'b'): 'q0',
            ('q1', 'a'): 'qERRO',
            ('qERRO', 'a'): 'qERRO',
            ('qERRO', 'b'): 'qERRO',
        }
    )


@pytest.mark.parametrize("cadeia,esperado", [
    ("",     True),
    ("ab",   True),
    ("abab", True),
    ("a",    False),
    ("ba",   False),
    ("aba",  False),
    ("b",    False),
])
def test_ab_star(dfa_ab_star, cadeia, esperado):
    aceito, passos = dfa_ab_star.aceita(cadeia)
    assert aceito == esperado


def test_contagem_passos(dfa_ab_star):
    _, passos = dfa_ab_star.aceita("abab")
    # 4 símbolos → 4 passos
    assert passos == 4


def test_trace_populado(dfa_ab_star):
    dfa_ab_star.aceita("ab")
    assert len(dfa_ab_star.trace) > 0
    assert any("resultado" in linha for linha in dfa_ab_star.trace)


def test_contrato_retorno(dfa_ab_star):
    resultado = dfa_ab_star.aceita("ab")
    assert isinstance(resultado, tuple) and len(resultado) == 2
    aceito, passos = resultado
    assert isinstance(aceito, bool)
    assert isinstance(passos, int)
