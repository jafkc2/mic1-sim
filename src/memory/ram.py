from __future__ import annotations

from typing import Iterable

from constantes import MASCARA_PALAVRA, TAMANHO_RAM


class MemoriaRAM:
    def __init__(self, tamanho: int = TAMANHO_RAM) -> None:
        if type(tamanho) is not int or tamanho <= 0:
            raise ValueError("O tamanho da RAM deve ser um inteiro positivo.")
        self.tamanho = tamanho
        self._palavras: list[int] = [0] * tamanho

    def _validar_endereco(self, endereco: int) -> None:
        if type(endereco) is not int or not (0 <= endereco < self.tamanho):
            raise ValueError(f"Endereco invalido: {endereco!r}. Intervalo: 0..{self.tamanho - 1}.")

    def normalizar_palavra(self, valor: int) -> int:
        if type(valor) is not int:
            raise TypeError("O conteudo de uma palavra deve ser inteiro.")
        return valor & MASCARA_PALAVRA

    _normalizar_palavra = normalizar_palavra

    def ler(self, endereco: int) -> int:
        self._validar_endereco(endereco)
        return self._palavras[endereco]

    def escrever(self, endereco: int, valor: int) -> None:
        self._validar_endereco(endereco)
        self._palavras[endereco] = self.normalizar_palavra(valor)

    def carregar(self, palavras: Iterable[int], endereco_inicial: int = 0) -> None:
        self._validar_endereco(endereco_inicial)
        valores = [self.normalizar_palavra(v) for v in palavras]
        if endereco_inicial + len(valores) > self.tamanho:
            raise ValueError("Programa ultrapassa os limites da RAM.")
        self._palavras[endereco_inicial:endereco_inicial + len(valores)] = valores

    def limpar(self) -> None:
        self._palavras = [0] * self.tamanho

    def visualizar(self, inicio: int = 0, quantidade: int = 16) -> list[tuple[int, int]]:
        if type(inicio) is not int or type(quantidade) is not int or quantidade < 0:
            raise ValueError("Inicio e quantidade devem ser inteiros validos.")
        if not (0 <= inicio <= self.tamanho) or inicio + quantidade > self.tamanho:
            raise ValueError("Intervalo fora da RAM.")
        return [(end, self._palavras[end]) for end in range(inicio, inicio + quantidade)]