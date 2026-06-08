from dataclasses import dataclass, field


@dataclass
class MT:
    """
    Simulador de Máquina de Turing determinística de uma fita.

    delta: {(estado, lido): (novo_estado, escrito, movimento)}
      movimento ∈ {'L', 'R', 'S'}
    blank: símbolo de branco (padrão '_')
    halt_accept: estado de aceitação
    halt_reject: estado de rejeição (opcional; se None, qualquer estado
                 sem transição definida é tratado como rejeição)
    max_steps: limite de segurança contra loops infinitos
    """
    states: set[str]
    alphabet: set[str]          # alfabeto da fita (inclui blank)
    input_alphabet: set[str]    # alfabeto de entrada (sem blank)
    start: str
    halt_accept: str
    halt_reject: str | None
    delta: dict[tuple[str, str], tuple[str, str, str]]
    blank: str = '_'
    max_steps: int = 100_000

    steps: int = field(default=0, init=False)
    trace: list[str] = field(default_factory=list, init=False)

    def aceita(self, s: str) -> tuple[bool, int]:
        """Retorna (aceito, passos). Um passo = um movimento da cabeça."""
        self.steps = 0
        self.trace = []

        fita: list[str] = list(s) if s else [self.blank]
        cabeca = 0
        estado = self.start

        self.trace.append(
            f"inicio: estado={estado} fita={''.join(fita)} cabeca={cabeca}"
        )

        while self.steps < self.max_steps:
            # Expande fita se necessário
            while cabeca >= len(fita):
                fita.append(self.blank)
            if cabeca < 0:
                fita.insert(0, self.blank)
                cabeca = 0

            lido = fita[cabeca]
            transicao = self.delta.get((estado, lido))
            self.steps += 1

            if transicao is None:
                # Sem transição: comportamento de rejeição
                self.trace.append(
                    f"passo {self.steps}: ({estado}, '{lido}') -> sem transição"
                )
                self.trace.append("resultado: rejeita")
                return False, self.steps

            novo_estado, escrito, mov = transicao
            fita[cabeca] = escrito

            self.trace.append(
                f"passo {self.steps}: ({estado}, '{lido}') -> "
                f"({novo_estado}, '{escrito}', {mov}) "
                f"fita={''.join(fita)} cabeca={cabeca + (1 if mov == 'R' else -1 if mov == 'L' else 0)}"
            )

            estado = novo_estado

            if estado == self.halt_accept:
                self.trace.append("resultado: aceita")
                return True, self.steps
            if self.halt_reject and estado == self.halt_reject:
                self.trace.append("resultado: rejeita")
                return False, self.steps

            if mov == 'R':
                cabeca += 1
            elif mov == 'L':
                cabeca -= 1
            # 'S' não move

        self.trace.append(f"resultado: limite de {self.max_steps} passos atingido (loop?)")
        return False, self.steps
