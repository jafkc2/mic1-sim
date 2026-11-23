from __future__ import annotations

from enum import Enum
from typing import NamedTuple
from constantes import BITS_PALAVRA


class OperacaoShifter(str, Enum):
    PASS = "PASS"
    SHL = "SHL"
    SHR = "SHR"
    ASHR = "ASHR"


class ResultadoShifter(NamedTuple):
    operacao: OperacaoShifter
    entrada: int
    deslocamento: int
    saida: int
    bit_descartado: int


class Shifter:
    ALIASES = {"": "PASS", "NONE": "PASS", "LSL": "SHL", "LEFT": "SHL",
               "LSR": "SHR", "RIGHT": "SHR", "ASR": "ASHR", "ARITH_RIGHT": "ASHR"}

    def __init__(self, largura_bits: int = BITS_PALAVRA) -> None:
        if type(largura_bits) is not int or largura_bits <= 0:
            raise ValueError("largura_bits deve ser um inteiro positivo.")
        self.largura_bits = largura_bits
        self.mascara = (1 << largura_bits) - 1
        self.bit_sinal = 1 << (largura_bits - 1)
        self.ultimo_resultado: ResultadoShifter | None = None

    def executar(self, valor: int, operacao: OperacaoShifter | str | None = OperacaoShifter.PASS,
                 bits: int = 1) -> int:
        if type(valor) is not int:
            raise TypeError("A entrada deve ser um inteiro.")
        if type(bits) is not int or bits < 0:
            raise ValueError("bits deve ser um inteiro nao negativo.")
        if not isinstance(operacao, OperacaoShifter):
            chave = "" if operacao is None else str(operacao).strip().upper()
            operacao = OperacaoShifter(self.ALIASES.get(chave, chave))
        entrada = valor & self.mascara
        sinal = bool(entrada & self.bit_sinal)
        if operacao == OperacaoShifter.PASS or bits == 0:
            saida, descartado = entrada, 0
        elif operacao == OperacaoShifter.SHL:
            saida = entrada << bits & self.mascara
            descartado = (entrada >> (self.largura_bits - bits)) & 1 if 0 < bits <= self.largura_bits else 0
        elif operacao in (OperacaoShifter.SHR, OperacaoShifter.ASHR):
            descartado = (entrada >> (bits - 1)) & 1 if 0 < bits <= self.largura_bits else (int(sinal) if operacao == OperacaoShifter.ASHR else 0)
            if operacao == OperacaoShifter.SHR:
                saida = entrada >> bits
            else:
                assinado = entrada - (1 << self.largura_bits) if sinal else entrada
                saida = (assinado >> bits) & self.mascara
        else:
            raise ValueError(f"Operacao nao suportada: {operacao}.")
        self.ultimo_resultado = ResultadoShifter(operacao, entrada, bits, saida, descartado)
        return saida

    def executar_detalhado(self, valor: int, operacao: OperacaoShifter | str | None = OperacaoShifter.PASS,
                            bits: int = 1) -> ResultadoShifter:
        self.executar(valor, operacao, bits)
        return self.ultimo_resultado
