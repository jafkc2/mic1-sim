"""RAM principal do MAC-I: 4.096 palavras de 16 bits, enderecadas por palavra.

Esta classe NAO conhece a GUI nem as caches. A CPU deve usar o controlador
para os acessos durante a simulacao; a RAM direta e util para carregar/resetar.
"""

from __future__ import annotations

from typing import Iterable

from config import MASCARA_PALAVRA, TAMANHO_RAM


class MemoriaRAM:
    def __init__(self, tamanho: int = TAMANHO_RAM) -> None:
        if type(tamanho) is not int or tamanho <= 0:
            raise ValueError("O tamanho da RAM deve ser um inteiro positivo.")
        self.tamanho = tamanho
        self._palavras: list[int] = [0] * tamanho

    """Verificação do endereço"""
    def _validar_endereco(self, endereco: int) -> None:
        if type(endereco) is not int or not (0 <= endereco < self.tamanho):
            raise ValueError(f"Endereco invalido: {endereco!r}. Intervalo: 0..{self.tamanho - 1}.")

    @staticmethod
    def _normalizar_palavra(valor: int) -> int:
        if type(valor) is not int:
            raise TypeError("O conteudo de uma palavra deve ser inteiro.")
        # O armazenamento e de 16 bits: -1, por exemplo, vira 0xFFFF.
        return valor & MASCARA_PALAVRA

    def ler(self, endereco: int) -> int:
        self._validar_endereco(endereco)
        return self._palavras[endereco]

    def escrever(self, endereco: int, valor: int) -> None:
        self._validar_endereco(endereco)
        self._palavras[endereco] = self._normalizar_palavra(valor)

    def carregar(self, palavras: Iterable[int], endereco_inicial: int = 0) -> None:
        """Carrega um programa/lista de palavras, sem apagar outras posicoes.

        Valida tudo antes de alterar a RAM, evitando carga parcial em caso de erro.
        """
        self._validar_endereco(endereco_inicial)
        valores = [self._normalizar_palavra(v) for v in palavras]
        if endereco_inicial + len(valores) > self.tamanho:
            raise ValueError("Programa ultrapassa os limites da RAM.")
        self._palavras[endereco_inicial:endereco_inicial + len(valores)] = valores

    def limpar(self) -> None:
        self._palavras = [0] * self.tamanho

    def visualizar(self, inicio: int = 0, quantidade: int = 16) -> list[tuple[int, int]]:
        """Retorna copia de um intervalo para futuro Treeview do Tkinter."""
        if type(inicio) is not int or type(quantidade) is not int or quantidade < 0:
            raise ValueError("Inicio e quantidade devem ser inteiros validos.")
        if not (0 <= inicio <= self.tamanho) or inicio + quantidade > self.tamanho:
            raise ValueError("Intervalo fora da RAM.")
        return [(end, self._palavras[end]) for end in range(inicio, inicio + quantidade)]
