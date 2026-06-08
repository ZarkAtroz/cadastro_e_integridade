"""
Testes da MT para L = {w#w | w ∈ {0,1}*} (src/recursiva.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
from automato import load_test_cases
from recursiva import build_ww_mt, INPUT_ALPHABET, TAPE_ALPHABET

# ---------------------------------------------------------------------------
# Parametrizados via arquivo .txt
# ---------------------------------------------------------------------------

_BASE = Path(__file__).parent.parent
_TXT = _BASE / 'testes' / 'testes_recursiva.txt'
_CASOS = load_test_cases(_TXT)


@pytest.mark.parametrize("cadeia,esperado", _CASOS, ids=[repr(c) for c, _ in _CASOS])
def test_ww_txt(cadeia, esperado):
    mt = build_ww_mt()
    aceito, _ = mt.aceita(cadeia)
    assert aceito == esperado, (
        f"cadeia={repr(cadeia)}: esperado={esperado}, obtido={aceito}\n"
        + "\n".join(mt.trace)
    )


# ---------------------------------------------------------------------------
# Testes estruturais
# ---------------------------------------------------------------------------

def test_numero_de_estados():
    # q_return foi dividido em q_return (direita) + q_return_l (esquerda)
    # para cruzar o # corretamente. Total: 12 estados operacionais + 2 halt.
    mt = build_ww_mt()
    assert len(mt.states) == 12, f"esperado 12 estados, obtido {mt.states}"


def test_estados_halt():
    mt = build_ww_mt()
    assert mt.halt_accept == 'q_accept'
    assert mt.halt_reject == 'q_reject'
    assert 'q_accept' in mt.states
    assert 'q_reject' in mt.states


def test_alfabeto_entrada():
    assert INPUT_ALPHABET == {'0', '1', '#'}


def test_alfabeto_fita():
    assert TAPE_ALPHABET == {'0', '1', '#', 'X', 'Y', '_'}


def test_todas_transicoes_referenciam_estados_existentes():
    """Nenhuma transição aponta para estado que não existe (typo detector)."""
    mt = build_ww_mt()
    for (estado, _), (proximo, _, _) in mt.delta.items():
        assert estado in mt.states, f"estado origem desconhecido: {estado}"
        assert proximo in mt.states, (
            f"transição ({estado}, ...) aponta para estado desconhecido: {proximo}"
        )


# ---------------------------------------------------------------------------
# Casos críticos explícitos
# ---------------------------------------------------------------------------

def test_caso_critico_w_vazio():
    """'#' deve ser aceita (w = ε de cada lado)."""
    mt = build_ww_mt()
    aceito, _ = mt.aceita("#")
    assert aceito, "'#' foi rejeitada\n" + "\n".join(mt.trace)


def test_caso_critico_entrada_vazia():
    """Cadeia vazia deve ser rejeitada (sem # nenhum)."""
    mt = build_ww_mt()
    aceito, _ = mt.aceita("")
    assert not aceito, "cadeia vazia foi aceita\n" + "\n".join(mt.trace)


def test_caso_critico_troca_bit_final():
    """10101#10100 deve ser rejeitada (último bit diferente)."""
    mt = build_ww_mt()
    aceito, _ = mt.aceita("10101#10100")
    assert not aceito, "10101#10100 foi aceita\n" + "\n".join(mt.trace)


def test_caso_critico_multiplos_hash():
    """0##0 deve ser rejeitada (# múltiplos)."""
    mt = build_ww_mt()
    aceito, _ = mt.aceita("0##0")
    assert not aceito, "0##0 foi aceita\n" + "\n".join(mt.trace)


def test_contrato_retorno():
    mt = build_ww_mt()
    resultado = mt.aceita("0#0")
    assert isinstance(resultado, tuple) and len(resultado) == 2
    aceito, passos = resultado
    assert isinstance(aceito, bool)
    assert isinstance(passos, int) and passos > 0
