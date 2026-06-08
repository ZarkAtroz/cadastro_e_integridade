"""
Utilitários de I/O compartilhados entre os três reconhecedores.
"""
from pathlib import Path


def load_test_cases(path: str | Path) -> list[tuple[str, bool]]:
    """
    Lê um arquivo de casos de teste no formato:

        cadeia<TAB>A|R

    Regras:
    - Linha completamente vazia (sem TAB) → ignorada.
    - Linha com TAB como primeiro caractere → cadeia vazia, lê o esperado.
    - Usa split('\\t', 1) para preservar o '#' literal (é símbolo da linguagem R).
    - Linhas com formato inválido levantam ValueError com número da linha.

    Retorna lista de (cadeia, esperado_bool).
    """
    casos: list[tuple[str, bool]] = []
    texto = Path(path).read_text(encoding='utf-8')

    for numero, linha in enumerate(texto.splitlines(), start=1):
        # Ignora linha completamente em branco
        if linha == '':
            continue

        partes = linha.split('\t', 1)

        if len(partes) != 2:
            raise ValueError(
                f"Formato inválido na linha {numero}: "
                f"esperado 'cadeia<TAB>A|R', obtido {repr(linha)}"
            )

        cadeia, marcador = partes[0], partes[1].strip()

        if marcador not in ('A', 'R'):
            raise ValueError(
                f"Marcador inválido na linha {numero}: "
                f"esperado 'A' ou 'R', obtido {repr(marcador)}"
            )

        casos.append((cadeia, marcador == 'A'))

    return casos
