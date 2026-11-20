from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from memory.config import BITS_PALAVRA, MASCARA_PALAVRA


class OperacaoShifter(str, Enum):
    PASS = "PASS"  # Sem deslocamento (00)
    SHL = "SHL"    # Deslocamento à esquerda (01)
    SHR = "SHR"    # Deslocamento à direita (1)
    ASHR = "ASHR"  # Deslocamento aritmético à direita (preserva sinal)


@dataclass(frozen=True)
class ResultadoShifter:
    operacao: OperacaoShifter
    entrada: int
    deslocamento: int
    saida: int
    bit_descartado: int


class Shifter:
    def __init__(self, largura_bits: int = BITS_PALAVRA) -> None:
        if type(largura_bits) is not int or largura_bits <= 0:
            raise ValueError("largura_bits deve ser um inteiro positivo.")
        self.largura_bits = largura_bits
        self.mascara = (1 << largura_bits) - 1 if largura_bits == BITS_PALAVRA else MASCARA_PALAVRA
        self.bit_sinal = 1 << (largura_bits - 1)
        self.ultimo_resultado: ResultadoShifter | None = None

    def _normalizar(self, valor: int) -> int:
        if type(valor) is not int:
            raise TypeError("A entrada do Shifter deve ser um inteiro.")
        return valor & self.mascara

    def _resolver_operacao(operacao: OperacaoShifter | str | None) -> OperacaoShifter:
        if operacao is None:
            return OperacaoShifter.PASS
        if isinstance(operacao, OperacaoShifter):
            return operacao
        chave = operacao.strip().upper()
        aliases = {
            "": OperacaoShifter.PASS,
            "NONE": OperacaoShifter.PASS,
            "LSL": OperacaoShifter.SHL,
            "LEFT": OperacaoShifter.SHL,
            "LSR": OperacaoShifter.SHR,
            "RIGHT": OperacaoShifter.SHR,
            "ASR": OperacaoShifter.ASHR,
            "ARITH_RIGHT": OperacaoShifter.ASHR,
        }
        if chave in aliases:
            return aliases[chave]
        return OperacaoShifter(chave)

    def executar(
        self,
        valor: int,
        operacao: OperacaoShifter | str | None = OperacaoShifter.PASS,
        bits: int = 1,
    ) -> ResultadoShifter:
        if type(bits) is not int or bits < 0:
            raise ValueError("bits deve ser um inteiro maior ou igual a zero.")

        op = self._resolver_operacao(operacao)
        entrada = self._normalizar(valor)

        if op == OperacaoShifter.PASS or bits == 0:
            saida = entrada
            bit_descartado = 0
        elif op == OperacaoShifter.SHL:
            if bits >= self.largura_bits:
                bit_descartado = (entrada >> (self.largura_bits - 1)) & 1 if bits == self.largura_bits else 0
                saida = 0
            else:
                bit_descartado = (entrada >> (self.largura_bits - bits)) & 1
                saida = (entrada << bits) & self.mascara
        elif op == OperacaoShifter.SHR:
            if bits >= self.largura_bits:
                bit_descartado = (entrada >> (self.largura_bits - 1)) & 1 if bits == self.largura_bits else 0
                saida = 0
            else:
                bit_descartado = (entrada >> (bits - 1)) & 1
                saida = (entrada >> bits) & self.mascara
        elif op == OperacaoShifter.ASHR:
            negativo = bool(entrada & self.bit_sinal)
            if bits >= self.largura_bits:
                bit_descartado = 1 if negativo else 0
                saida = self.mascara if negativo else 0
            else:
                bit_descartado = (entrada >> (bits - 1)) & 1
                deslocado = entrada >> bits
                if negativo:
                    mascara_sinal = ((1 << bits) - 1) << (self.largura_bits - bits)
                    saida = (deslocado | mascara_sinal) & self.mascara
                else:
                    saida = deslocado & self.mascara
        else:
            raise ValueError(f"Operação do Shifter não suportada: {operacao!r}")

        resultado = ResultadoShifter(
            operacao=op,
            entrada=entrada,
            deslocamento=bits,
            saida=saida,
            bit_descartado=bit_descartado,
        )
        self.ultimo_resultado = resultado
        return resultado