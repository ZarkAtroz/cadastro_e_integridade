"""
Testes do DFA CPF (src/regular.py).
Carrega testes/testes_regular.txt via load_test_cases() + testes estruturais.
"""
import sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
from automato import load_test_cases
from regular import build_cpf_dfa, TRAP, PADRAO

# ---------------------------------------------------------------------------
# Testes parametrizados via arquivo .txt
# ---------------------------------------------------------------------------

_BASE = Path(__file__).parent.parent
_TXT = _BASE / 'testes' / 'testes_regular.txt'
_CASOS = load_test_cases(_TXT)


@pytest.mark.parametrize("cadeia,esperado", _CASOS, ids=[repr(c) for c, _ in _CASOS])
def test_cpf_txt(cadeia, esperado):
    dfa = build_cpf_dfa()
    aceito, _ = dfa.aceita(cadeia)
    assert aceito == esperado, (
        f"cadeia={repr(cadeia)}: esperado={esperado}, obtido={aceito}\n"
        + "\n".join(dfa.trace)
    )


# ---------------------------------------------------------------------------
# Testes estruturais
# ---------------------------------------------------------------------------

def test_numero_de_estados():
    dfa = build_cpf_dfa()
    # q0..q14 (15 estados) + q_trap = 16
    assert len(dfa.states) == 16


def test_trap_e_absorvente():
    """Qualquer símbolo no trap deve permanecer no trap."""
    dfa = build_cpf_dfa()
    for s in dfa.alphabet:
        assert dfa.delta.get((TRAP, s)) == TRAP, f"trap não absorve '{s}'"


def test_unico_estado_final():
    dfa = build_cpf_dfa()
    assert dfa.accept == {'q14'}


def test_comprimento_padrao():
    """PADRAO deve ter 14 posições (11 dígitos + 2 pontos + 1 hífen)."""
    assert len(PADRAO) == 14


def test_contagem_passos_cpf_valido():
    """CPF válido deve consumir exatamente 14 passos."""
    dfa = build_cpf_dfa()
    _, passos = dfa.aceita("123.456.789-00")
    assert passos == 14


def test_simbolo_fora_alfabeto_nao_levanta_excecao():
    """Símbolo fora de Σ não pode levantar exceção - vai pro trap."""
    dfa = build_cpf_dfa()
    try:
        aceito, passos = dfa.aceita("abc!@#")
        assert not aceito
        assert passos > 0
    except Exception as e:
        pytest.fail(f"aceita() levantou exceção para símbolo fora de Σ: {e}")


def test_trace_populado():
    dfa = build_cpf_dfa()
    dfa.aceita("123.456.789-00")
    assert any("resultado" in linha for linha in dfa.trace)


def test_contrato_retorno():
    dfa = build_cpf_dfa()
    resultado = dfa.aceita("123.456.789-00")
    assert isinstance(resultado, tuple) and len(resultado) == 2
    aceito, passos = resultado
    assert isinstance(aceito, bool)
    assert isinstance(passos, int)
