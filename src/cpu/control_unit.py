from __future__ import annotations

from cpu.microprogram import Condicao, Microinstrucao, ROM


class UnidadeControle:
    def __init__(self) -> None:
        self.rom = tuple(ROM)
        self._mir_rom = [
            Microinstrucao.decodificar(palavra)
            if palavra is not None else None
            for palavra in self.rom
        ]
        self.reset()

    def reset(self) -> None:
        self.mpc = 0
        self.mir: Microinstrucao | None = None
        self.endereco_mir: int | None = None
        self.em_execucao = False

    def buscar_microinstrucao(self) -> Microinstrucao:
        if 0 <= self.mpc < len(self._mir_rom):
            mir = self._mir_rom[self.mpc]
            if mir is not None:
                self.mir = mir
                self.endereco_mir = self.mpc
                self.em_execucao = True
                return mir
        raise RuntimeError(
            f"Endereco de controle invalido ou nao programado: {self.mpc}"
        )

    def calcular_proximo_endereco(self, flag_n: bool, flag_z: bool) -> int:
        if self.mir is None or self.endereco_mir is None:
            return 0
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
