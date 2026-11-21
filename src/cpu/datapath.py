from __future__ import annotations

from cpu.ula import ULA, OperacaoULA
from cpu.shifter import Shifter, OperacaoShifter
from memory.config import TAMANHO_RAM


class DataPath:
    def __init__(self) -> None:
        self.ula = ULA()
        self.shifter = Shifter()

        self.flag_z = False
        self.flag_n = False

        self.pc = 0
        self.ac = 0
        self.sp = TAMANHO_RAM
        self.ir = 0
        self.tir = 0

        self.c0 = 0
        self.cmais1 = 1
        self.cmenos1 = 0xFFFF
        self.amask = 0x0FFF
        self.smask = 0x00FF

        self.mbr = 0
        self.mar = 0

        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.f = 0

    def ler_barramento_a(self, usar_mbr: bool = False) -> int:
        if usar_mbr:
            return self.mbr
        return self.a

    def ler_barramento_b(self, reg: int | str) -> int:
        regs = self.get_registradores()
        if isinstance(reg, int):
            nomes = ["PC", "AC", "SP", "IR", "TIR", "0", "+1", "-1", "AMASK", "SMASK", "A", "B", "C", "D", "E", "F"]
            if 0 <= reg < len(nomes):
                reg = nomes[reg]
        return regs.get(str(reg).upper(), 0)

    def executar(
        self,
        valor_a: int,
        valor_b: int,
        op_ula: OperacaoULA | str,
        op_shifter: OperacaoShifter | str = "PASS",
    ) -> int:
        res_ula = self.ula.executar(valor_a, valor_b, op_ula)
        self.flag_z = res_ula.z
        self.flag_n = res_ula.n
        res_shifter = self.shifter.executar(res_ula.saida, op_shifter)
        return res_shifter.saida

    def escrever_barramento_c(self, valor: int, destinos: str | int | list[str | int]) -> None:
        valor = valor & 0xFFFF
        if isinstance(destinos, (str, int)):
            destinos = [destinos]

        nomes = ["PC", "AC", "SP", "IR", "TIR", "0", "+1", "-1", "AMASK", "SMASK", "A", "B", "C", "D", "E", "F"]

        for reg in destinos:
            if isinstance(reg, int) and 0 <= reg < len(nomes):
                reg = nomes[reg]

            reg = str(reg).upper()

            if reg == "PC":
                self.pc = valor
            elif reg == "AC":
                self.ac = valor
            elif reg == "SP":
                self.sp = valor
            elif reg == "IR":
                self.ir = valor
            elif reg == "TIR":
                self.tir = valor
            elif reg == "MAR":
                self.mar = valor & 0x0FFF
            elif reg == "MBR":
                self.mbr = valor
            elif reg == "A":
                self.a = valor
            elif reg == "B":
                self.b = valor
            elif reg == "C":
                self.c = valor
            elif reg == "D":
                self.d = valor
            elif reg == "E":
                self.e = valor
            elif reg == "F":
                self.f = valor

    def reset(self) -> None:
        self.flag_z = False
        self.flag_n = False
        self.pc = 0
        self.ac = 0
        self.sp = TAMANHO_RAM
        self.ir = 0
        self.tir = 0
        self.mbr = 0
        self.mar = 0
        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.f = 0

    def get_registradores(self) -> dict[str, int]:
        return {
            "PC": self.pc,
            "AC": self.ac,
            "SP": self.sp,
            "IR": self.ir,
            "TIR": self.tir,
            "0": self.c0,
            "+1": self.cmais1,
            "-1": self.cmenos1,
            "AMASK": self.amask,
            "SMASK": self.smask,
            "MBR": self.mbr,
            "MAR": self.mar,
            "A": self.a,
            "B": self.b,
            "C": self.c,
            "D": self.d,
            "E": self.e,
            "F": self.f,
        }

    def get_flags(self) -> dict[str, bool]:
        return {
            "N": self.flag_n,
            "Z": self.flag_z,
        }
