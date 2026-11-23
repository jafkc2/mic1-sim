import customtkinter as ctk

from cpu.cpu import CPU
from .barra_execucao import BarraExecucao
from .abas.simulador import AbaSimulador
from .abas.microarquitetura import PainelDatapath
from .abas.unidade_controle import PainelMicroprograma
from .abas.caches import PainelCache
from .abas.memoria import PainelMemoria


class TelaPrincipal(ctk.CTkFrame):
    def __init__(self, master, cpu: CPU):
        super().__init__(master)
        self.cpu = cpu
        self.abas = ctk.CTkTabview(self, corner_radius=9)
        self.abas.pack(fill="both", expand=True, padx=4, pady=4)

        aba_simulador = self.abas.add("Simulador")
        aba_datapath = self.abas.add("Microarquitetura")
        aba_microprograma = self.abas.add("Unidade de Controle")
        aba_cache = self.abas.add("Caches")
        aba_ram = self.abas.add("Memória RAM")

        self.simulador = AbaSimulador(
            aba_simulador,
            cpu,
            self._atualizar_graficos,
        )
        self.simulador.pack(fill="both", expand=True)

        self.painel_registradores = self.simulador.painel_registradores
        self.painel_estado = self.simulador.painel_estado
        self.painel_codigo = self.simulador.painel_codigo
        self.painel_controle = self.simulador.painel_controle
        self.painel_memoria = self.simulador.painel_memoria

        aba_datapath.grid_columnconfigure(0, weight=1)
        aba_datapath.grid_rowconfigure(0, weight=1)
        self.painel_datapath = PainelDatapath(aba_datapath, cpu)
        self.painel_datapath.grid(row=0, column=0, sticky="nsew")

        aba_microprograma.grid_columnconfigure(0, weight=1)
        aba_microprograma.grid_rowconfigure(0, weight=1)
        self.painel_microprograma = PainelMicroprograma(aba_microprograma, cpu)
        self.painel_microprograma.grid(row=0, column=0, sticky="nsew")

        aba_cache.grid_columnconfigure(0, weight=1)
        aba_cache.grid_rowconfigure(0, weight=1)
        self.painel_cache = PainelCache(aba_cache, cpu)
        self.painel_cache.grid(row=0, column=0, sticky="nsew")

        aba_ram.grid_columnconfigure(0, weight=1)
        aba_ram.grid_rowconfigure(0, weight=1)
        self.painel_memoria_completa = PainelMemoria(aba_ram, cpu=cpu)
        self.painel_memoria_completa.grid(row=0, column=0, sticky="nsew")

        self.barra_execucao = BarraExecucao(self, self)
        self.barra_execucao.pack(fill="x", padx=8, pady=(0, 6))
        self.simulador._atualizar_status = self._atualizar_barras
        self._atualizar_barras()

        self.atualizar()

    def _atualizar_barras(self, _texto=None):
        self.barra_execucao.atualizar_estado()

    def _atualizar_graficos(self):
        self.painel_datapath.atualizar()
        self.painel_microprograma.atualizar()
        self.painel_cache.atualizar()
        self.painel_memoria_completa.atualizar()
        self.barra_execucao.atualizar_estado()

    def atualizar(self):
        self.simulador.atualizar()
