from __future__ import annotations

from cpu.microprogram import Condicao, Microinstrucao, ROM, TAMANHO_ROM


class UnidadeControle:
    def __init__(self, rom: tuple[int | None, ...] = ROM) -> None:
        self.rom = tuple(rom)
        if len(self.rom) != TAMANHO_ROM:
            raise ValueError("A memoria de controle deve ter 256 posicoes.")
        for palavra in self.rom:
            if palavra is not None:
                Microinstrucao.decodificar(palavra)
        self.reset()

    def reset(self) -> None:
        self.mpc = 0
        self.mir: Microinstrucao | None = None
        self.endereco_mir: int | None = None
        self.em_execucao = False

    def buscar_microinstrucao(self) -> Microinstrucao:
        if self.em_execucao:
            raise RuntimeError("A microinstrucao atual ainda nao foi concluida.")
        if type(self.mpc) is not int or not 0 <= self.mpc < TAMANHO_ROM:
            raise ValueError(f"Endereco de controle invalido: {self.mpc!r}.")
        palavra = self.rom[self.mpc]
        if palavra is None:
            raise RuntimeError(f"Endereco de controle nao programado: {self.mpc}.")
        self.mir = Microinstrucao.decodificar(palavra)
        self.endereco_mir = self.mpc
        self.em_execucao = True
        return self.mir

    def calcular_proximo_endereco(self, flag_n: bool, flag_z: bool) -> int:
        if not self.em_execucao or self.mir is None or self.endereco_mir is None:
            raise RuntimeError("Nenhuma microinstrucao em execucao.")
        cond = self.mir.cond
        desviar = (
            cond == Condicao.SEMPRE
            or (cond == Condicao.NEGATIVO and flag_n)
            or (cond == Condicao.ZERO and flag_z)
        )
        if desviar:
            return self.mir.addr
        return (self.endereco_mir + 1) & 0xFF

    def avancar(self, flag_n: bool, flag_z: bool) -> int:
        self.mpc = self.calcular_proximo_endereco(flag_n, flag_z)
        self.em_execucao = False
        return self.mpc

    def get_sinais(self) -> dict[str, int]:
        if self.mir is None:
            return {}
        return self.mir.sinais()
