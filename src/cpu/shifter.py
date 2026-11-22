from __future__ import annotations

from enum import Enum

from constantes import BITS_PALAVRA


class OperacaoShifter(str, Enum):
    PASS = "PASS"
    SHL = "SHL"
    SHR = "SHR"


class Shifter:
    def __init__(self, largura_bits: int = BITS_PALAVRA) -> None:
        self.largura_bits = largura_bits
        self.mascara = (1 << largura_bits) - 1

    def executar(self, valor: int,
                 operacao: OperacaoShifter = OperacaoShifter.PASS) -> int:
        valor &= self.mascara
        if isinstance(operacao, str):
            operacao = OperacaoShifter(operacao)
        if operacao == OperacaoShifter.PASS:
            return valor
        if operacao == OperacaoShifter.SHL:
            return (valor << 1) & self.mascara
        if operacao == OperacaoShifter.SHR:
            return valor >> 1
        raise ValueError(f"Operacao do Shifter nao suportada: {operacao!r}")
