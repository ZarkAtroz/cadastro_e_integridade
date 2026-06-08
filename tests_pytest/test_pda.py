"""
Smoke test PDA: reconhece aⁿbⁿ (n >= 1).
Aceita: "ab", "aabb", "aaabbb"
Rejeita: "", "a", "b", "aab", "abb", "ba"
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from automato import PDA


@pytest.fixture
def pda_an_bn():
    """
    PDA para aⁿbⁿ (n >= 1):
      q0 -a,$/A$-> q0  (empilha A ao ler primeiro 'a')
      q0 -a,A/AA-> q0  (empilha A ao ler 'a' subsequente)
      q0 -b,A/ε -> q1  (começa desempilhar)
      q1 -b,A/ε -> q1  (continua desempilhar)
      q1 -ε,$/$-> q2   (fundo de pilha: aceita)
    """
    return PDA(
        alphabet={'a', 'b'},
        states={'q0', 'q1', 'q2'},
        start='q0',
        accept={'q2'},
        delta={
            ('q0', 'a', '$'): {('q0', 'A$')},   # primeiro 'a': empilha A mantendo $
            ('q0', 'a', 'A'): {('q0', 'AA')},   # 'a' subsequente: empilha A
            ('q0', 'b', 'A'): {('q1', '')},      # primeiro 'b': desempilha A
            ('q1', 'b', 'A'): {('q1', '')},      # 'b' subsequente: desempilha A
            ('q1', '',  '$'): {('q2', '$')},     # ε no fundo (só em q1): aceita
        },
        bottom='$',
    )


@pytest.mark.parametrize("cadeia,esperado", [
    ("ab",     True),
    ("aabb",   True),
    ("aaabbb", True),
    ("",       False),
    ("a",      False),
    ("b",      False),
    ("aab",    False),
    ("abb",    False),
    ("ba",     False),
])
def test_an_bn(pda_an_bn, cadeia, esperado):
    aceito, passos = pda_an_bn.aceita(cadeia)
    assert aceito == esperado, (
        f"cadeia={repr(cadeia)}: esperado={esperado}, obtido={aceito}\n"
        + "\n".join(pda_an_bn.trace)
    )


def test_passos_positivos(pda_an_bn):
    _, passos = pda_an_bn.aceita("aabb")
    assert passos > 0


def test_trace_populado(pda_an_bn):
    pda_an_bn.aceita("ab")
    assert len(pda_an_bn.trace) > 0
    assert any("resultado" in linha for linha in pda_an_bn.trace)


def test_contrato_retorno(pda_an_bn):
    resultado = pda_an_bn.aceita("ab")
    assert isinstance(resultado, tuple) and len(resultado) == 2
    aceito, passos = resultado
    assert isinstance(aceito, bool)
    assert isinstance(passos, int)
