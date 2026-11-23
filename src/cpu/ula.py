from __future__ import annotations

from enum import Enum
from typing import NamedTuple
from constantes import BITS_PALAVRA


class OperacaoULA(str, Enum):
    ADD = "ADD"
    SUB = "SUB"
    AND = "AND"
    OR = "OR"
    XOR = "XOR"
    PASS_A = "A"
    PASS_B = "B"
    NOT_A = "NOT_A"
    NOT_B = "NOT_B"
    INC_A = "INC_A"
    DEC_A = "DEC_A"


class ResultadoULA(NamedTuple):
    operacao: OperacaoULA
    a: int
    b: int
    saida: int
    n: bool
    z: bool
    carry: bool


class ULA:
    ALIASES = {"+": "ADD", "-": "SUB", "&": "AND", "|": "OR", "^": "XOR",
               "~A": "NOT_A", "~B": "NOT_B", "A+1": "INC_A", "A-1": "DEC_A"}

    def __init__(self, largura_bits: int = BITS_PALAVRA) -> None:
        if type(largura_bits) is not int or largura_bits <= 0:
            raise ValueError("largura_bits deve ser um inteiro positivo.")
        self.largura_bits = largura_bits
        self.mascara = (1 << largura_bits) - 1
        self.bit_sinal = 1 << (largura_bits - 1)
        self.ultimo_resultado: ResultadoULA | None = None

    def executar(self, a: int, b: int = 0,
                 operacao: OperacaoULA | str = OperacaoULA.ADD) -> tuple[int, bool, bool]:
        if type(a) is not int or type(b) is not int:
            raise TypeError("Os operandos da ULA devem ser inteiros.")
        if not isinstance(operacao, OperacaoULA):
            chave = str(operacao).strip().upper()
            operacao = OperacaoULA(self.ALIASES.get(chave, chave))
        a, b = a & self.mascara, b & self.mascara
        carry = False
        if operacao in (OperacaoULA.ADD, OperacaoULA.SUB, OperacaoULA.INC_A, OperacaoULA.DEC_A):
            operando = 1 if operacao in (OperacaoULA.INC_A, OperacaoULA.DEC_A) else b
            subtrair = operacao in (OperacaoULA.SUB, OperacaoULA.DEC_A)
            bruto = a - operando if subtrair else a + operando
            carry = (a >= operando) if subtrair else (bruto > self.mascara)
            saida = bruto & self.mascara
        elif operacao == OperacaoULA.AND:
            saida = a & b
        elif operacao == OperacaoULA.OR:
            saida = a | b
        elif operacao == OperacaoULA.XOR:
            saida = a ^ b
        elif operacao == OperacaoULA.PASS_A:
            saida = a
        elif operacao == OperacaoULA.PASS_B:
            saida = b
        elif operacao == OperacaoULA.NOT_A:
            saida = ~a & self.mascara
        elif operacao == OperacaoULA.NOT_B:
            saida = ~b & self.mascara
        else:
            raise ValueError(f"Operacao nao suportada: {operacao}.")
        n, z = bool(saida & self.bit_sinal), saida == 0
        self.ultimo_resultado = ResultadoULA(operacao, a, b, saida, n, z, carry)
        return saida, n, z

    def executar_detalhado(self, a: int, b: int, operacao: OperacaoULA | str) -> ResultadoULA:
        self.executar(a, b, operacao)
        return self.ultimo_resultado
