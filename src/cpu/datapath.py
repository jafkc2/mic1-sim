from __future__ import annotations

from cpu.ula import ULA, OperacaoULA
from cpu.shifter import Shifter, OperacaoShifter
from cpu.microprogram import Microinstrucao
from constantes import TAMANHO_RAM, MASCARA_PALAVRA


class DataPath:
    NOMES_REGISTRADORES = (
        "PC", "AC", "SP", "IR", "TIR", "0", "+1", "-1",
        "AMASK", "SMASK", "A", "B", "C", "D", "E", "F",
    )
    ATRIBUTOS = {
        "PC": "pc", "AC": "ac", "SP": "sp", "IR": "ir", "TIR": "tir",
        "0": "c0", "+1": "cmais1", "-1": "cmenos1", "AMASK": "amask",
        "SMASK": "smask", "A": "a", "B": "b", "C": "c", "D": "d",
        "E": "e", "F": "f", "MAR": "mar", "MBR": "mbr",
    }
    CONSTANTES = frozenset(("0", "+1", "-1", "AMASK", "SMASK"))

    def __init__(self) -> None:
        self.ula = ULA()
        self.shifter = Shifter()
        self.reset()

    def reset(self) -> None:
        for atributo in self.ATRIBUTOS.values():
            setattr(self, atributo, 0)
        self.sp = TAMANHO_RAM
        self.cmais1 = 1
        self.cmenos1 = MASCARA_PALAVRA
        self.amask = TAMANHO_RAM - 1
        self.smask = 0x00FF
        self.flag_n = False
        self.flag_z = False
        self.barramento_a = 0
        self.barramento_b = 0
        self.barramento_c = 0
        self.latch_a = 0
        self.latch_b = 0
        self.saida_amux = 0
        self.saida_ula = 0
        self.microinstrucao_ativa: Microinstrucao | None = None
        self.etapa = 0

    @classmethod
    def _resolver_registrador(cls, reg: int) -> int:
        if not 0 <= reg < len(cls.NOMES_REGISTRADORES):
            raise ValueError(f"Codigo de registrador invalido: {reg}.")
        return reg

    @staticmethod
    def _palavra(valor: int) -> int:
        if type(valor) is not int:
            raise TypeError("O valor do registrador deve ser inteiro.")
        return valor & MASCARA_PALAVRA

    def ler_registrador(self, reg: int) -> int:
        reg = self._resolver_registrador(reg)
        nome = self.NOMES_REGISTRADORES[reg]
        return getattr(self, self.ATRIBUTOS[nome])

    def ler_barramento_a(self, reg: int = 10, usar_mbr: bool = False) -> int:
        if usar_mbr:
            return self.mbr
        reg = self._resolver_registrador(reg)
        self.barramento_a = self.ler_registrador(reg)
        return self.barramento_a

    def ler_barramento_b(self, reg: int) -> int:
        reg = self._resolver_registrador(reg)
        self.barramento_b = self.ler_registrador(reg)
        return self.barramento_b

    def escrever_barramento_c(self, valor: int,
                              destinos: int | list[int]) -> None:
        valor = self._palavra(valor)
        if type(destinos) is int:
            destinos = [destinos]
        if not isinstance(destinos, list):
            raise TypeError("O destino deve ser um codigo inteiro ou uma lista de codigos.")
        registradores = [self._resolver_registrador(reg) for reg in destinos]
        self.barramento_c = valor
        for reg in registradores:
            nome = self.NOMES_REGISTRADORES[reg]
            if nome in self.CONSTANTES:
                continue
            setattr(self, self.ATRIBUTOS[nome], valor)

    def selecionar_amux(self, sinal: int) -> int:
        if sinal not in (0, 1):
            raise ValueError("AMUX deve ser 0 ou 1.")
        self.saida_amux = self.mbr if sinal else self.latch_a
        return self.saida_amux

    def executar(
        self,
        valor_a: int,
        valor_b: int,
        op_ula: OperacaoULA | str,
        op_shifter: OperacaoShifter = OperacaoShifter.PASS,
    ) -> int:
        saida, flag_n, flag_z = self.ula.executar(
            valor_a, valor_b, op_ula
        )
        saida = self.shifter.executar(saida, op_shifter)
        self.saida_ula = saida
        self.flag_z = flag_z
        self.flag_n = flag_n
        self.barramento_c = saida
        return self.barramento_c

    def carregar_latches(self, microinstrucao: Microinstrucao) -> None:
        if self.etapa != 0:
            raise RuntimeError("O Datapath ainda possui uma microinstrucao em andamento.")

        self.latch_a = self.ler_barramento_a(microinstrucao.a)
        self.latch_b = self.ler_barramento_b(microinstrucao.b)
        self.microinstrucao_ativa = microinstrucao
        self.etapa = 2

    def processar_microinstrucao(self) -> int:
        mi = self.microinstrucao_ativa
        if self.etapa != 2 or mi is None:
            raise RuntimeError("Os latches devem ser carregados antes do processamento.")
        valor_a = self.selecionar_amux(mi.amux)
        resultado = self.executar(valor_a, self.latch_b, mi.operacao_ula, mi.operacao_shifter)
        if mi.mar:
            self.mar = self.latch_b & (TAMANHO_RAM - 1)
        self.etapa = 3
        return resultado

    def gravar_resultado(self) -> None:
        mi = self.microinstrucao_ativa
        if self.etapa != 3 or mi is None:
            raise RuntimeError("A microinstrucao deve ser processada antes da escrita.")
        resultado = self.barramento_c
        if mi.enc:
            self.escrever_barramento_c(resultado, mi.c)
        if mi.mbr:
            self.mbr = resultado
        self.microinstrucao_ativa = None
        self.etapa = 0

    def get_endereco_memoria(self) -> int:
        return self.mar & (TAMANHO_RAM - 1)

    def get_dado_memoria(self) -> int:
        return self.mbr & MASCARA_PALAVRA

    def get_registradores(self) -> dict[str, int]:
        nomes = (*self.NOMES_REGISTRADORES[:10], "MBR", "MAR", *self.NOMES_REGISTRADORES[10:])
        codigo = (*range(10), -1, -1, *range(10, 16))
        resultado = {}
        for nome, reg in zip(nomes, codigo):
            if nome == "MBR":
                resultado[nome] = self.mbr
            elif nome == "MAR":
                resultado[nome] = self.mar
            else:
                resultado[nome] = self.ler_registrador(reg)
        return resultado

    def get_flags(self) -> dict[str, bool]:
        return {"N": self.flag_n, "Z": self.flag_z}

    def get_barramentos(self) -> dict[str, int]:
        return {"A": self.barramento_a, "B": self.barramento_b, "C": self.barramento_c}

    def get_latches(self) -> dict[str, int]:
        return {"A": self.latch_a, "B": self.latch_b}

    def set_dado_memoria(self, valor: int) -> None:
        self.mbr = self._palavra(valor)