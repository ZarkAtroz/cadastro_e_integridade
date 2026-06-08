"""
Bateria unificada de testes — Projeto Linguagens Formais.
Roda os três reconhecedores contra seus arquivos .txt e imprime tabela + traces.

Uso:
    python src/testes.py               # bateria completa + passo a passo
    python src/testes.py --quiet       # só resumos por linguagem e total
    python src/testes.py --no-trace    # tabela sem passo a passo
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).parent))

from automato import load_test_cases
from regular import build_cpf_dfa
from livre_contexto import build_balanceado_pda
from recursiva import build_ww_mt

# ---------------------------------------------------------------------------
# Configuração das baterias
# ---------------------------------------------------------------------------

BASE = Path(__file__).parent.parent

# (rótulo, factory, arquivo_txt, cadeia_trace_aceita, cadeia_trace_rejeitada)
BATERIAS: list[tuple[str, Callable, str, str, str]] = [
    (
        "LR  -- CPF (ddd.ddd.ddd-dd)",
        build_cpf_dfa,
        str(BASE / "testes" / "testes_regular.txt"),
        "123.456.789-00",
        "12.345.678-90",
    ),
    (
        "LLC -- Parenteses balanceados",
        build_balanceado_pda,
        str(BASE / "testes" / "testes_livre_contexto.txt"),
        "({a+b})",
        "((a+b)",
    ),
    (
        "R   -- w#w  (w em {0,1}*)",
        build_ww_mt,
        str(BASE / "testes" / "testes_recursiva.txt"),
        "01#01",
        "0#1",
    ),
]

# ---------------------------------------------------------------------------
# Validação de entrada
# ---------------------------------------------------------------------------

MAX_LEN = 10_000


def _valida_cadeia(cadeia: str, origem: str) -> None:
    """Levanta SystemExit com mensagem descritiva se a cadeia for inválida."""
    if len(cadeia) > MAX_LEN:
        print(
            f"ERRO: cadeia em '{origem}' excede {MAX_LEN} caracteres "
            f"(tamanho={len(cadeia)}).",
            file=sys.stderr,
        )
        sys.exit(2)
    # Cadeia vazia é válida; isprintable() retorna True para strings vazias
    if cadeia and not cadeia.isprintable():
        print(
            f"ERRO: cadeia em '{origem}' contém caracteres não-imprimíveis.",
            file=sys.stderr,
        )
        sys.exit(2)


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------

# Detecta suporte a UTF-8; usa ASCII se terminal não suportar
_UTF8 = (getattr(sys.stdout, "encoding", "") or "").lower().replace("-", "") == "utf8"

SEP  = ("═" if _UTF8 else "=") * 60
SEP2 = ("─" if _UTF8 else "-") * 60
_OK  = "✓" if _UTF8 else "[OK]"
_XX  = "✗" if _UTF8 else "[XX]"

COL_CADEIA  = 26
COL_ESP     = 8
COL_OBT     = 8
COL_PASSOS  = 8


def _linha_tabela(cadeia: str, esperado: bool, obtido: bool, passos: int) -> str:
    ok = _OK if esperado == obtido else _XX
    c_repr  = repr(cadeia).ljust(COL_CADEIA)
    c_esp   = ("A" if esperado else "R").ljust(COL_ESP)
    c_obt   = ("A" if obtido  else "R").ljust(COL_OBT)
    c_pass  = str(passos).ljust(COL_PASSOS)
    return f"  {c_repr}  {c_esp}  {c_obt}  {c_pass}  {ok}"


def _cabecalho_tabela() -> str:
    c = "Cadeia".ljust(COL_CADEIA)
    e = "Esperado".ljust(COL_ESP)
    o = "Obtido".ljust(COL_OBT)
    p = "Passos".ljust(COL_PASSOS)
    return f"  {c}  {e}  {o}  {p}  OK?"


# ---------------------------------------------------------------------------
# Execução principal
# ---------------------------------------------------------------------------

def rodar_bateria(
    rotulo: str,
    factory: Callable,
    txt_path: str,
    trace_aceita: str,
    trace_rejeita: str,
    quiet: bool,
    no_trace: bool,
) -> tuple[int, int]:
    """
    Executa uma bateria completa para um reconhecedor.
    Retorna (ok_count, total).
    """
    casos = load_test_cases(txt_path)
    ok = 0

    if not quiet:
        print(SEP)
        print(f" {rotulo}")
        print(SEP)
        print(_cabecalho_tabela())
        print(f"  {SEP2}")

    for cadeia, esperado in casos:
        _valida_cadeia(cadeia, txt_path)
        rec = factory()
        obtido, passos = rec.aceita(cadeia)
        if obtido == esperado:
            ok += 1
        if not quiet:
            print(_linha_tabela(cadeia, esperado, obtido, passos))

    if not quiet:
        print(f"  {SEP2}")
        print(f"  Aprovacao: {ok}/{len(casos)}")
        print()

    # Passo a passo
    if not no_trace:
        for cadeia_trace, label in [(trace_aceita, "ACEITA"), (trace_rejeita, "REJEITA")]:
            _valida_cadeia(cadeia_trace, "trace")
            rec = factory()
            obtido, passos = rec.aceita(cadeia_trace)
            print(f"  Trace — cadeia {label}: {repr(cadeia_trace)}")
            print(f"  {SEP2}")
            for linha in rec.trace:
                print(f"    {linha}")
            print()

    return ok, len(casos)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bateria unificada — três reconhecedores (LR, LLC, R)"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Exibe apenas os resumos, sem tabelas nem traces"
    )
    parser.add_argument(
        "--no-trace", action="store_true", dest="no_trace",
        help="Exibe tabelas mas omite o passo a passo"
    )
    args = parser.parse_args()

    total_ok = 0
    total = 0

    for rotulo, factory, txt, tr_a, tr_r in BATERIAS:
        ok, n = rodar_bateria(
            rotulo, factory, txt, tr_a, tr_r,
            quiet=args.quiet,
            no_trace=args.no_trace,
        )
        if args.quiet:
            print(f"  {rotulo:<40} {ok}/{n}")
        total_ok += ok
        total    += n

    print(SEP)
    status = f"{_OK} TODOS PASSARAM" if total_ok == total else f"{_XX} FALHAS ENCONTRADAS"
    print(f"  TOTAL: {total_ok}/{total}  {status}")
    print(SEP)

    sys.exit(0 if total_ok == total else 1)


if __name__ == "__main__":
    main()
