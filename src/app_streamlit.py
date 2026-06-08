"""
Bonus 2 - Interface Streamlit para os tres reconhecedores.

Uso:
    streamlit run src/app_streamlit.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from regular import build_cpf_dfa
from livre_contexto import build_balanceado_pda
from recursiva import build_ww_mt

# ---------------------------------------------------------------------------
# Cache dos reconhecedores (st.cache_resource: objetos nao-serializaveis)
# ---------------------------------------------------------------------------

@st.cache_resource
def get_cpf_dfa():
    """Retorna instancia cacheada do DFA de CPF."""
    return build_cpf_dfa()


@st.cache_resource
def get_balanceado_pda():
    """Retorna instancia cacheada do PDA de parenteses balanceados."""
    return build_balanceado_pda()


@st.cache_resource
def get_ww_mt():
    """Retorna instancia cacheada da MT para w#w."""
    return build_ww_mt()


# ---------------------------------------------------------------------------
# Funcao unica de renderizacao de aba
# ---------------------------------------------------------------------------

def render_aba(
    aba_id: str,
    descricao: str,
    placeholder: str,
    reconhecedor_factory: Callable,
    aceitas: list[str],
    rejeitadas: list[str],
) -> None:
    """
    Renderiza uma aba completa com input, exemplos, validacao e trace.

    aba_id: chave unica usada no session_state (ex: 'lr', 'llc', 'r').
    """
    key = f"input_{aba_id}"

    # Inicializa session_state antes do widget
    if key not in st.session_state:
        st.session_state[key] = ""

    st.markdown(descricao)

    # Exemplos clicaveis
    st.markdown("**Exemplos:**")
    col_a, col_r = st.columns(2)

    with col_a:
        st.markdown("*Aceitas*")
        for exemplo in aceitas:
            if st.button(exemplo, key=f"btn_{aba_id}_a_{exemplo}"):
                st.session_state[key] = exemplo
                st.rerun()

    with col_r:
        st.markdown("*Rejeitadas*")
        for exemplo in rejeitadas:
            if st.button(exemplo, key=f"btn_{aba_id}_r_{exemplo}"):
                st.session_state[key] = exemplo
                st.rerun()

    st.markdown("---")

    # Input da cadeia
    cadeia = st.text_input(
        "Cadeia:",
        placeholder=placeholder,
        key=key,
    )

    mostrar_trace = st.checkbox("Mostrar trace", key=f"trace_{aba_id}")

    if st.button("Validar", key=f"validar_{aba_id}", type="primary"):
        rec = reconhecedor_factory()
        aceito, passos = rec.aceita(cadeia)

        if aceito:
            st.success(f"aceita - {passos} passos")
        else:
            st.error(f"rejeita - {passos} passos")

        if mostrar_trace:
            st.code("\n".join(rec.trace), language="")


# ---------------------------------------------------------------------------
# Layout principal
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Reconhecedores - Linguagens Formais",
    page_icon="A",
    layout="centered",
)

st.title("Reconhecedores de Linguagens Formais")
st.markdown(
    "Demonstracao da hierarquia de Chomsky **LR ⊊ LLC ⊊ R** "
    "com tres reconhecedores implementados como simuladores explicitos de automato: "
    "DFA (CPF), PDA (parenteses balanceados) e Maquina de Turing (w\\#w)."
)

tabs = st.tabs(["LR - CPF", "LLC - Parenteses", "R - w#w"])

with tabs[0]:
    render_aba(
        aba_id="lr",
        descricao=(
            "**DFA** - Valida o formato textual do CPF: `ddd.ddd.ddd-dd`.  \n"
            "Nao verifica os digitos verificadores (isso tornaria o problema nao-regular)."
        ),
        placeholder="123.456.789-00",
        reconhecedor_factory=get_cpf_dfa,
        aceitas=["123.456.789-00", "000.000.000-00", "999.888.777-66"],
        rejeitadas=["12.345.678-90", "123-456-789.00", "12a.456.789-00"],
    )

with tabs[1]:
    render_aba(
        aba_id="llc",
        descricao=(
            "**PDA** - Verifica se os delimitadores `()`, `[]`, `{}` estao "
            "balanceados e corretamente pareados.  \n"
            "Aceita letras, digitos e operadores no meio. Cadeia vazia e aceita."
        ),
        placeholder="((x+y)*z)",
        reconhecedor_factory=get_balanceado_pda,
        aceitas=["((x+y)*z)", "{[()]}", "()()"],
        rejeitadas=["((a+b)", "([)]", "((("],
    )

with tabs[2]:
    render_aba(
        aba_id="r",
        descricao=(
            "**Maquina de Turing** - Reconhece `L = {w#w | w ∈ {0,1}*}`.  \n"
            "A cadeia deve ser `w` seguida de `#` e a mesma sequencia `w`.  \n"
            "Caso especial: `#` (w = vazio) e aceito."
        ),
        placeholder="101#101",
        reconhecedor_factory=get_ww_mt,
        aceitas=["101#101", "00#00", "#"],
        rejeitadas=["0#1", "01#10", "010"],
    )

st.markdown("---")
st.markdown(
    "Repositório GitHub: [cadastro_e_integridade](https://github.com/ZarkAtroz/cadastro_e_integridade) "
    "&nbsp;|&nbsp; Projeto Final - Linguagens Formais"
)
