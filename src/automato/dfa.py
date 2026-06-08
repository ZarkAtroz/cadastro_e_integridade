from dataclasses import dataclass, field


@dataclass
class DFA:
    """
    Simulador de Autômato Finito Determinístico.

    delta: tabela de transição {(estado, símbolo): próximo_estado}

    Símbolo fora do alfabeto nunca levanta exceção: é tratado como transição
    indefinida. Se `trap` estiver definido, o simulador drena para ele e
    continua absorvendo os símbolos restantes (contabilizando cada passo).
    Caso `trap` seja None, rejeita imediatamente ao encontrar o símbolo.

    trap: nome do estado sumidouro (sink); se None, rejeição imediata.
    """
    alphabet: set[str]
    states: set[str]
    start: str
    accept: set[str]
    delta: dict[tuple[str, str], str]
    trap: str | None = None

    steps: int = field(default=0, init=False)
    trace: list[str] = field(default_factory=list, init=False)

    def aceita(self, s: str) -> tuple[bool, int]:
        """
        Retorna (aceito, passos).
        Um passo = leitura de um símbolo com mudança (ou manutenção) de estado.
        """
        self.steps = 0
        self.trace = []
        estado = self.start
        self.trace.append(f"inicio: estado={estado}")

        for simbolo in s:
            self.steps += 1

            # Consulta a tabela; símbolo fora do alfabeto resulta em None
            proximo = self.delta.get((estado, simbolo))

            if proximo is None:
                if self.trap is not None:
                    # Drena para trap e continua absorvendo (não para aqui)
                    self.trace.append(
                        f"passo {self.steps}: ({estado}, '{simbolo}') -> {self.trap}"
                        f"  [símbolo {'fora de Σ' if simbolo not in self.alphabet else 'sem transição'}]"
                    )
                    estado = self.trap
                else:
                    self.trace.append(
                        f"passo {self.steps}: ({estado}, '{simbolo}') -> REJEITA"
                        f"  [símbolo {'fora de Σ' if simbolo not in self.alphabet else 'sem transição'}]"
                    )
                    self.trace.append("resultado: rejeita")
                    return False, self.steps
            else:
                self.trace.append(
                    f"passo {self.steps}: ({estado}, '{simbolo}') -> {proximo}"
                )
                estado = proximo

        aceito = estado in self.accept
        self.trace.append(
            f"resultado: {'aceita' if aceito else 'rejeita'} (estado final={estado})"
        )
        return aceito, self.steps
