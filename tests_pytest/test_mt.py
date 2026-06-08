"""
Smoke test MT: reconhece 0*1* (zero ou mais 0s seguidos de zero ou mais 1s).
Aceita: "", "0", "1", "01", "0011", "000111"
Rejeita: "10", "010", "101"
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from automato import MT


@pytest.fixture
def mt_0star_1star():
    """
    MT para 0*1*:
    q0: lê 0s → permanece q0
    q0: lê 1 → vai q1
    q0: lê _ → vai qACEITA (cadeia só de 0s ou vazia)
    q1: lê 1 → permanece q1
    q1: lê _ → vai qACEITA
    q1: lê 0 → vai qREJEITA (0 após 1: inválido)
    """
    return MT(
        states={'q0', 'q1', 'qACEITA', 'qREJEITA'},
        alphabet={'0', '1', '_'},
        input_alphabet={'0', '1'},
        start='q0',
        halt_accept='qACEITA',
        halt_reject='qREJEITA',
        delta={
            ('q0', '0'): ('q0', '0', 'R'),
            ('q0', '1'): ('q1', '1', 'R'),
            ('q0', '_'): ('qACEITA', '_', 'S'),
            ('q1', '1'): ('q1', '1', 'R'),
            ('q1', '_'): ('qACEITA', '_', 'S'),
            ('q1', '0'): ('qREJEITA', '0', 'S'),
        },
        blank='_',
    )


@pytest.mark.parametrize("cadeia,esperado", [
    ("",      True),
    ("0",     True),
    ("1",     True),
    ("01",    True),
    ("0011",  True),
    ("10",    False),
    ("010",   False),
    ("101",   False),
])
def test_0star_1star(mt_0star_1star, cadeia, esperado):
    aceito, passos = mt_0star_1star.aceita(cadeia)
    assert aceito == esperado, (
        f"cadeia={repr(cadeia)}: esperado={esperado}, obtido={aceito}\n"
        + "\n".join(mt_0star_1star.trace)
    )


def test_passos_proporcional(mt_0star_1star):
    _, passos_curto = mt_0star_1star.aceita("01")
    _, passos_longo = mt_0star_1star.aceita("0011")
    assert passos_longo > passos_curto


def test_trace_populado(mt_0star_1star):
    mt_0star_1star.aceita("01")
    assert len(mt_0star_1star.trace) > 0
    assert any("resultado" in linha for linha in mt_0star_1star.trace)


def test_contrato_retorno(mt_0star_1star):
    resultado = mt_0star_1star.aceita("01")
    assert isinstance(resultado, tuple) and len(resultado) == 2
    aceito, passos = resultado
    assert isinstance(aceito, bool)
    assert isinstance(passos, int)
