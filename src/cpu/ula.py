from __future__ import annotations

from enum import Enum

from constantes import BITS_PALAVRA


class OperacaoULA(str, Enum):
    ADD = "ADD"      # A + B
    AND = "AND"      # A & B
    PASS_A = "A"     # A
    NOT_A = "NOT_A"  # ~A


class ULA:
    def __init__(self, largura_bits: int = BITS_PALAVRA) -> None:
        self.largura_bits = largura_bits
        self.mascara = (1 << largura_bits) - 1
        self.bit_sinal = 1 << (largura_bits - 1)

    def executar(self, a: int, b: int,
                 operacao: OperacaoULA | str) -> tuple[int, bool, bool]:
        a &= self.mascara
        b &= self.mascara
        if isinstance(operacao, str):
            operacao = OperacaoULA(operacao)
        if operacao == OperacaoULA.ADD:
            saida = (a + b) & self.mascara
        elif operacao == OperacaoULA.AND:
            saida = (a & b) & self.mascara
        elif operacao == OperacaoULA.PASS_A:
            saida = a
        elif operacao == OperacaoULA.NOT_A:
            saida = (~a) & self.mascara
        else:
            raise ValueError(f"Operação da ULA não suportada: {operacao!r}")
        return saida, bool(saida & self.bit_sinal), saida == 0