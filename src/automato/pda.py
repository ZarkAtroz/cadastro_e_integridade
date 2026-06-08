from collections import deque
from dataclasses import dataclass, field


# Configuração PDA: (estado, posição_na_entrada, pilha_como_tupla)
# Usada para detectar loops em ε-transições.
Config = tuple[str, int, tuple[str, ...]]


@dataclass
class PDA:
    """
    Simulador de Autômato de Pilha Não-Determinístico (BFS sobre configurações).

    delta: {(estado, símbolo|'', topo_pilha|'') -> set[(novo_estado, push_string)]}
      - símbolo=''  → ε-transição de entrada
      - topo_pilha='' → não consome topo (lê sem pop)
      - push_string='' → não empilha nada (pop puro)
      - push_string='XY' → empilha Y depois X (X fica no topo)

    Símbolo especial '$' usado como fundo de pilha.
    Um passo = uma transição aplicada (push/pop/leitura).
    """
    alphabet: set[str]
    states: set[str]
    start: str
    accept: set[str]
    delta: dict[tuple[str, str, str], set[tuple[str, str]]]
    # Chave: (estado_atual, símbolo_entrada|'', topo_pilha|'')
    bottom: str = '$'

    steps: int = field(default=0, init=False)
    trace: list[str] = field(default_factory=list, init=False)

    def aceita(self, s: str) -> tuple[bool, int]:
        """Retorna (aceito, passos). Passos = total de transições exploradas."""
        self.steps = 0
        self.trace = []

        # Fila BFS: (estado, posição_entrada, pilha, passos_locais, caminho)
        pilha_inicial = (self.bottom,)
        fila: deque[tuple[str, int, tuple[str, ...], int, list[str]]] = deque()
        fila.append((self.start, 0, pilha_inicial, 0, [f"inicio: estado={self.start} pilha={list(pilha_inicial)}"]))

        visitados: set[Config] = set()

        melhor_caminho: list[str] = []
        melhor_passos = 0

        while fila:
            estado, pos, pilha, passos_locais, caminho = fila.popleft()

            cfg: Config = (estado, pos, pilha)
            if cfg in visitados:
                continue
            visitados.add(cfg)

            # Verifica aceitação: entrada consumida e estado final
            if pos == len(s) and estado in self.accept:
                self.steps = passos_locais
                self.trace = caminho + [f"resultado: aceita"]
                return True, self.steps

            # Guarda melhor caminho (mais longo explorado) para trace de rejeição
            if passos_locais > melhor_passos:
                melhor_passos = passos_locais
                melhor_caminho = caminho

            topo = pilha[-1] if pilha else ''

            for (estado_delta, simbulo_delta, topo_delta), destinos in self.delta.items():
                if estado_delta != estado:
                    continue
                # simbulo_delta pode ser '' (ε) ou um símbolo real
                consome_entrada = simbulo_delta != ''
                if consome_entrada:
                    if pos >= len(s) or s[pos] != simbulo_delta:
                        continue
                    novo_pos = pos + 1
                else:
                    novo_pos = pos

                # topo_delta pode ser '' (ignora topo) ou símbolo específico
                if topo_delta != '':
                    if not pilha or pilha[-1] != topo_delta:
                        continue
                    pilha_sem_topo = pilha[:-1]
                else:
                    pilha_sem_topo = pilha

                for (novo_estado, push) in destinos:
                    # Constrói nova pilha: push empilhado da direita pra esquerda
                    if push:
                        nova_pilha = pilha_sem_topo + tuple(reversed(push))
                    else:
                        nova_pilha = pilha_sem_topo

                    novo_passos = passos_locais + 1
                    self.steps = max(self.steps, novo_passos)

                    desc_trans = (
                        f"passo {novo_passos}: ({estado}, "
                        f"{'ε' if not simbulo_delta else repr(simbulo_delta)}, "
                        f"{'ε' if not topo_delta else repr(topo_delta)}) -> "
                        f"({novo_estado}, {repr(push) if push else 'ε'}) "
                        f"pilha={list(nova_pilha)}"
                    )
                    nova_config: Config = (novo_estado, novo_pos, nova_pilha)
                    if nova_config not in visitados:
                        fila.append((novo_estado, novo_pos, nova_pilha, novo_passos, caminho + [desc_trans]))

        self.trace = melhor_caminho + ["resultado: rejeita"]
        return False, self.steps
