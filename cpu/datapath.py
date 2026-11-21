#mudei
# falta: 1- função para ler do barramento B. 2- função para gravar do barramento c. 3- funções para ler e escrever memória com mar e mbr.
from __future__ import annotations

from cpu.ula import ULA, OperacaoULA, ResultadoULA
from cpu.shifter import Shifter, OperacaoShifter, ResultadoShifter
from memory.config import TAMANHO_RAM


class DataPath:
    def __init__(self):
        self.ula = ULA()
        self.shifter = Shifter()

        self.flag_z: bool = False
        self.flag_n: bool = False

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
        self.mpc = 0
        self.mdr = 0

        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.f = 0

    def executar_operacao(
        self,
        valor_a: int,
        valor_b: int = 0,
        op_ula: OperacaoULA | str = OperacaoULA.ADD,
        op_shifter: OperacaoShifter | str | None = OperacaoShifter.PASS,
        bits_shifter: int = 1,
    ) -> int:
        res_ula = self.ula.executar(valor_a, valor_b, operacao=op_ula)
        
        self.flag_n = res_ula.n
        self.flag_z = res_ula.z

        res_shifter = self.shifter.executar(
            res_ula.saida,
            operacao=op_shifter,
            bits=bits_shifter,
        )

        return res_shifter.saida

    def get_flags(self) -> dict[str, bool]:
        return {
            "N": self.flag_n,
            "Z": self.flag_z,
        }

    def get_registradores(self):
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
            "MPC": self.mpc,
            "MDR": self.mdr,
            "A": self.a,
            "B": self.b,
            "C": self.c,
            "D": self.d,
            "E": self.e,
            "F": self.f
        }