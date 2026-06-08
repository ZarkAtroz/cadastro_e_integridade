"""
Testes do PDA para delimitadores balanceados (src/livre_contexto.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
from automato import load_test_cases
from livre_contexto import build_balanceado_pda, ABRIDORES, FECHADORES

# ---------------------------------------------------------------------------
# Parametrizados via arquivo .txt
# ---------------------------------------------------------------------------

_BASE = Path(__file__).parent.parent
_TXT = _BASE / 'testes' / 'testes_livre_contexto.txt'
_CASOS = load_test_cases(_TXT)


@pytest.mark.parametrize("cadeia,esperado", _CASOS, ids=[repr(c) for c, _ in _CASOS])
def test_balanceado_txt(cadeia, esperado):
    pda = build_balanceado_pda()
    aceito, _ = pda.aceita(cadeia)
    assert aceito == esperado, (
        f"cadeia={repr(cadeia)}: esperado={esperado}, obtido={aceito}\n"
        + "\n".join(pda.trace)
    )


# ---------------------------------------------------------------------------
# Testes estruturais
# ---------------------------------------------------------------------------

def test_numero_de_estados():
    pda = build_balanceado_pda()
    assert len(pda.states) == 2, f"esperado 2 estados, obtido {pda.states}"


def test_epsilon_transicao_de_aceitacao_existe():
    pda = build_balanceado_pda()
    assert ('q', '', '$') in pda.delta, "ε-transição (q,'','$') ausente na delta"
    destinos = pda.delta[('q', '', '$')]
    assert ('q_f', '$') in destinos


def test_transicoes_cruzadas_ausentes():
    """Fechador com topo de abridor diferente NÃO deve existir na delta."""
    pda = build_balanceado_pda()
    pares_cruzados = [
        ('q', ')', '['), ('q', ')', '{'),
        ('q', ']', '('), ('q', ']', '{'),
        ('q', '}', '('), ('q', '}', '['),
    ]
    for chave in pares_cruzados:
        assert chave not in pda.delta, (
            f"transição cruzada {chave} não deveria existir na delta"
        )


# ---------------------------------------------------------------------------
# Casos críticos explícitos
# ---------------------------------------------------------------------------

def test_caso_critico_cruzado():
    """([)] deve ser rejeitada - pareamento cruzado."""
    pda = build_balanceado_pda()
    aceito, _ = pda.aceita("([)]")
    assert not aceito, "([)] foi aceita incorretamente\n" + "\n".join(pda.trace)


def test_caso_critico_concatenacao():
    """()() deve ser aceita - concatenação no topo é válida."""
    pda = build_balanceado_pda()
    aceito, _ = pda.aceita("()()")
    assert aceito, "()() foi rejeitada incorretamente\n" + "\n".join(pda.trace)


def test_caso_critico_abridores_sem_fechamento():
    """((( deve ser rejeitada - abridores sem fechador."""
    pda = build_balanceado_pda()
    aceito, _ = pda.aceita("(((")
    assert not aceito, "((( foi aceita incorretamente\n" + "\n".join(pda.trace)


def test_contrato_retorno():
    pda = build_balanceado_pda()
    resultado = pda.aceita("()")
    assert isinstance(resultado, tuple) and len(resultado) == 2
    aceito, passos = resultado
    assert isinstance(aceito, bool)
    assert isinstance(passos, int) and passos > 0
