from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from cpu.ula import OperacaoULA
from cpu.shifter import OperacaoShifter


class Registrador(IntEnum):
    PC = 0
    AC = 1
    SP = 2
    IR = 3
    TIR = 4
    ZERO = 5
    UM = 6
    MENOS_UM = 7
    AMASK = 8
    SMASK = 9
    A = 10
    B = 11
    C = 12
    D = 13
    E = 14
    F = 15


class Condicao(IntEnum):
    SEQUENCIAL = 0
    NEGATIVO = 1
    ZERO = 2
    SEMPRE = 3


CAMPOS = (
    ("amux", 1), ("cond", 2), ("alu", 2), ("sh", 2),
    ("mbr", 1), ("mar", 1), ("rd", 1), ("wr", 1), ("enc", 1),
    ("c", 4), ("b", 4), ("a", 4), ("addr", 8),
)


@dataclass(frozen=True)
class Microinstrucao:
    amux: int = 0
    cond: int = Condicao.SEQUENCIAL
    alu: int = 2
    sh: int = 0
    mbr: int = 0
    mar: int = 0
    rd: int = 0
    wr: int = 0
    enc: int = 0
    c: int = Registrador.ZERO
    b: int = Registrador.ZERO
    a: int = Registrador.ZERO
    addr: int = 0

    def __post_init__(self) -> None:
        for nome, bits in CAMPOS:
            valor = getattr(self, nome)
            if not isinstance(valor, int) or not 0 <= valor < (1 << bits):
                raise ValueError(f"Campo {nome} invalido: {valor!r}.")
        if self.sh == 3:
            raise ValueError("Codigo SH=3 nao utilizado no MIC-1.")

    def codificar(self) -> int:
        palavra = 0
        for nome, bits in CAMPOS:
            palavra = (palavra << bits) | getattr(self, nome)
        return palavra

    @classmethod
    def decodificar(cls, palavra: int) -> Microinstrucao:
        if type(palavra) is not int or not 0 <= palavra < (1 << 32):
            raise ValueError("A microinstrucao deve ser uma palavra de 32 bits.")
        campos = {}
        for nome, bits in reversed(CAMPOS):
            campos[nome] = palavra & ((1 << bits) - 1)
            palavra >>= bits
        return cls(**campos)

    @property
    def operacao_ula(self) -> OperacaoULA:
        return (OperacaoULA.ADD, OperacaoULA.AND,
                OperacaoULA.PASS_A, OperacaoULA.NOT_A)[self.alu]

    @property
    def operacao_shifter(self) -> OperacaoShifter:
        return (OperacaoShifter.PASS, OperacaoShifter.SHL,
                OperacaoShifter.SHR)[self.sh]

    def sinais(self) -> dict[str, int]:
        return {nome.upper(): int(getattr(self, nome)) for nome, _ in CAMPOS}


PC, AC, SP, IR, TIR, ZERO, UM, MENOS_UM, AMASK, SMASK, A, B, C, D, E, F = Registrador
N = Condicao.NEGATIVO
Z = Condicao.ZERO
GOTO = Condicao.SEMPRE


def _m(*, a=ZERO, b=ZERO, destino=None, alu=2, sh=0, amux=0,
       mar=0, mbr=0, rd=0, wr=0, cond=0, addr=0) -> Microinstrucao:
    return Microinstrucao(
        amux=amux, cond=cond, alu=alu, sh=sh, mbr=mbr, mar=mar,
        rd=rd, wr=wr, enc=int(destino is not None),
        c=ZERO if destino is None else destino, b=b, a=a, addr=addr,
    )


MICROPROGRAMA = (
    _m(b=PC, mar=1, rd=1),
    _m(a=PC, b=UM, alu=0, destino=PC, rd=1),
    _m(amux=1, destino=IR, cond=N, addr=28),
    _m(a=IR, b=IR, alu=0, sh=1, destino=TIR, cond=N, addr=19),
    _m(a=TIR, sh=1, destino=TIR, cond=N, addr=11),
    _m(a=TIR, cond=N, addr=9),
    _m(b=IR, mar=1, rd=1),
    _m(rd=1),
    _m(amux=1, destino=AC, cond=GOTO, addr=0),
    _m(a=AC, b=IR, mar=1, mbr=1, wr=1),
    _m(wr=1, cond=GOTO, addr=0),
    _m(a=TIR, cond=N, addr=15),
    _m(b=IR, mar=1, rd=1),
    _m(rd=1),
    _m(amux=1, b=AC, alu=0, destino=AC, cond=GOTO, addr=0),
    _m(b=IR, mar=1, rd=1),
    _m(a=AC, b=UM, alu=0, destino=AC, rd=1),
    _m(amux=1, alu=3, destino=A),
    _m(a=AC, b=A, alu=0, destino=AC, cond=GOTO, addr=0),
    _m(a=TIR, sh=1, destino=TIR, cond=N, addr=25),
    _m(a=TIR, cond=N, addr=23),
    _m(a=AC, cond=N, addr=0),
    _m(a=IR, b=AMASK, alu=1, destino=PC, cond=GOTO, addr=0),
    _m(a=AC, cond=Z, addr=22),
    _m(cond=GOTO, addr=0),
    _m(a=TIR, cond=N, addr=27),
    _m(a=IR, b=AMASK, alu=1, destino=PC, cond=GOTO, addr=0),
    _m(a=IR, b=AMASK, alu=1, destino=AC, cond=GOTO, addr=0),
    _m(a=IR, b=IR, alu=0, sh=1, destino=TIR, cond=N, addr=40),
    _m(a=TIR, sh=1, destino=TIR, cond=N, addr=35),
    _m(a=TIR, cond=N, addr=33),
    _m(a=IR, b=SP, alu=0, destino=A),
    _m(b=A, mar=1, rd=1, cond=GOTO, addr=7),
    _m(a=IR, b=SP, alu=0, destino=A),
    _m(a=AC, b=A, mar=1, mbr=1, wr=1, cond=GOTO, addr=10),
    _m(a=TIR, cond=N, addr=38),
    _m(a=IR, b=SP, alu=0, destino=A),
    _m(b=A, mar=1, rd=1, cond=GOTO, addr=13),
    _m(a=IR, b=SP, alu=0, destino=A),
    _m(b=A, mar=1, rd=1, cond=GOTO, addr=16),
    _m(a=TIR, sh=1, destino=TIR, cond=N, addr=46),
    _m(a=TIR, cond=N, addr=44),
    _m(a=AC, cond=N, addr=22),
    _m(cond=GOTO, addr=0),
    _m(a=AC, cond=Z, addr=0),
    _m(a=IR, b=AMASK, alu=1, destino=PC, cond=GOTO, addr=0),
    _m(a=TIR, sh=1, destino=TIR, cond=N, addr=50),
    _m(a=SP, b=MENOS_UM, alu=0, destino=SP),
    _m(a=PC, b=SP, mar=1, mbr=1, wr=1),
    _m(a=IR, b=AMASK, alu=1, destino=PC, wr=1, cond=GOTO, addr=0),
    _m(a=TIR, sh=1, destino=TIR, cond=N, addr=65),
    _m(a=TIR, sh=1, destino=TIR, cond=N, addr=59),
    _m(a=TIR, cond=N, addr=56),
    _m(b=AC, mar=1, rd=1),
    _m(a=SP, b=MENOS_UM, alu=0, destino=SP, rd=1),
    _m(b=SP, mar=1, wr=1, cond=GOTO, addr=10),
    _m(a=UM, b=SP, alu=0, destino=SP, mar=1, rd=1),
    _m(rd=1),
    _m(b=AC, mar=1, wr=1, cond=GOTO, addr=10),
    _m(a=TIR, cond=N, addr=62),
    _m(a=SP, b=MENOS_UM, alu=0, destino=SP),
    _m(a=AC, b=SP, mar=1, mbr=1, wr=1, cond=GOTO, addr=10),
    _m(a=UM, b=SP, alu=0, destino=SP, mar=1, rd=1),
    _m(rd=1),
    _m(amux=1, destino=AC, cond=GOTO, addr=0),
    _m(a=TIR, sh=1, destino=TIR, cond=N, addr=73),
    _m(a=TIR, cond=N, addr=70),
    _m(a=UM, b=SP, alu=0, destino=SP, mar=1, rd=1),
    _m(rd=1),
    _m(amux=1, destino=PC, cond=GOTO, addr=0),
    _m(a=AC, destino=A),
    _m(a=SP, destino=AC),
    _m(a=A, destino=SP, cond=GOTO, addr=0),
    _m(a=TIR, cond=N, addr=76),
    _m(a=IR, b=SMASK, alu=1, destino=A),
    _m(a=SP, b=A, alu=0, destino=SP, cond=GOTO, addr=0),
    _m(a=IR, b=SMASK, alu=1, destino=A),
    _m(a=A, alu=3, destino=A),
    _m(a=A, b=UM, alu=0, destino=A, cond=GOTO, addr=75),
)

TAMANHO_ROM = 256
ROM = tuple(mi.codificar() for mi in MICROPROGRAMA) + (None,) * (
    TAMANHO_ROM - len(MICROPROGRAMA)
)
