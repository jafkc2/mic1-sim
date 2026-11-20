from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from memory.config import BITS_PALAVRA, MASCARA_PALAVRA


class OperacaoULA(str, Enum):
    ADD = "ADD"      # A + B
    SUB = "SUB"      # A - B
    AND = "AND"      # A & B
    OR = "OR"        # A | B
    XOR = "XOR"      # A ^ B
    PASS_A = "A"     # A
    PASS_B = "B"     # B
    NOT_A = "NOT_A"  # ~A
    NOT_B = "NOT_B"  # ~B
    INC_A = "INC_A"  # A + 1
    DEC_A = "DEC_A"  # A - 1


class ResultadoULA:
    operacao: OperacaoULA
    a: int
    b: int
    saida: int
    n: bool  # Flag Negativo
    z: bool  # Flag Zero (saida == 0)
    carry: bool  # Carry/borrow útil para depuração e exibição gráfica


class ULA:
    def __init__(self, largura_bits: int = BITS_PALAVRA) -> None:
        if type(largura_bits) is not int or largura_bits <= 0:
            raise ValueError("largura_bits deve ser um inteiro positivo.")
        self.largura_bits = largura_bits
        self.mascara = (1 << largura_bits) - 1 if largura_bits == BITS_PALAVRA else MASCARA_PALAVRA
        self.bit_sinal = 1 << (largura_bits - 1)
        self.ultimo_resultado: ResultadoULA | None = None

    def _normalizar(self, valor: int) -> int:
        if type(valor) is not int:
            raise TypeError("Os operandos da ULA devem ser inteiros.")
        return valor & self.mascara

    def _resolver_operacao(self, operacao: OperacaoULA | str) -> OperacaoULA:
        if isinstance(operacao, OperacaoULA):
            return operacao
        chave = operacao.strip().upper()
        aliases = {
            "+": OperacaoULA.ADD,
            "-": OperacaoULA.SUB,
            "&": OperacaoULA.AND,
            "|": OperacaoULA.OR,
            "^": OperacaoULA.XOR,
            "~A": OperacaoULA.NOT_A,
            "~B": OperacaoULA.NOT_B,
            "A+1": OperacaoULA.INC_A,
            "A-1": OperacaoULA.DEC_A,
        }
        if chave in aliases:
            return aliases[chave]
        return OperacaoULA(chave)

    def executar(
        self,
        a: int,
        b: int = 0,
        operacao: OperacaoULA | str = OperacaoULA.ADD,
    ) -> ResultadoULA:
        op = self._resolver_operacao(operacao)
        val_a = self._normalizar(a)
        val_b = self._normalizar(b)
        carry = False

        if op == OperacaoULA.ADD:
            soma_bruta = val_a + val_b
            carry = soma_bruta > self.mascara
            saida = soma_bruta & self.mascara
        elif op == OperacaoULA.SUB:
            diff_bruta = val_a - val_b
            carry = val_a >= val_b
            saida = diff_bruta & self.mascara
        elif op == OperacaoULA.AND:
            saida = (val_a & val_b) & self.mascara
        elif op == OperacaoULA.OR:
            saida = (val_a | val_b) & self.mascara
        elif op == OperacaoULA.XOR:
            saida = (val_a ^ val_b) & self.mascara
        elif op == OperacaoULA.PASS_A:
            saida = val_a
        elif op == OperacaoULA.PASS_B:
            saida = val_b
        elif op == OperacaoULA.NOT_A:
            saida = (~val_a) & self.mascara
        elif op == OperacaoULA.NOT_B:
            saida = (~val_b) & self.mascara
        elif op == OperacaoULA.INC_A:
            soma_bruta = val_a + 1
            carry = soma_bruta > self.mascara
            saida = soma_bruta & self.mascara
        elif op == OperacaoULA.DEC_A:
            diff_bruta = val_a - 1
            carry = val_a > 0
            saida = diff_bruta & self.mascara
        else:
            raise ValueError(f"Operação da ULA não suportada: {operacao!r}")

        resultado = ResultadoULA(
            operacao=op,
            a=val_a,
            b=val_b,
            saida=saida,
            n=bool(saida & self.bit_sinal),
            z=(saida == 0),
            carry=carry,
        )
        self.ultimo_resultado = resultado
        return resultado