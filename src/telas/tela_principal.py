import customtkinter as ctk

from cpu.cpu import CPU
from .painel_codigo import PainelCodigo
from .painel_controle import PainelControle
from .painel_cache import PainelCache
from .painel_datapath import PainelDatapath
from .painel_estado_cpu import PainelEstadoCPU
from .painel_memoria import PainelMemoria
from .painel_microprograma import PainelMicroprograma
from .painel_registradores import PainelRegistradores


class TelaSimulador(ctk.CTkFrame):
    def __init__(self, master, cpu: CPU, atualizar_graficos):
        super().__init__(master, fg_color="transparent")
        self.cpu = cpu
        self._atualizar_graficos = atualizar_graficos
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.painel_registradores = PainelRegistradores(self)
        self.painel_registradores.grid(row=0, column=0, padx=7, pady=7, sticky="nsew")

        self.painel_estado = PainelEstadoCPU(self)
        self.painel_estado.grid(row=0, column=1, padx=7, pady=7, sticky="nsew")

        self.painel_codigo = PainelCodigo(self)
        self.painel_codigo.grid(row=1, column=0, padx=7, pady=7, sticky="nsew")

        self.painel_controle = PainelControle(self)
        self.painel_controle.grid(row=1, column=1, padx=7, pady=7, sticky="nsew")

        self.painel_memoria = PainelMemoria(self.painel_estado, compacto=True)
        self.painel_memoria.grid(row=4, column=0, columnspan=2,
                                padx=8, pady=6, sticky="nsew")

    def atualizar(self):
        self.painel_registradores.atualizar()
        self.painel_estado.atualizar()
        self.painel_memoria.atualizar()
        self.painel_controle.atualizar_botoes()
        self._atualizar_graficos()


class BarraExecucao(ctk.CTkFrame):
    def __init__(self, master, tela):
        super().__init__(master, fg_color="#122237", corner_radius=7)
        self.tela = tela
        self.grid_columnconfigure(5, weight=1)
        self._botoes = {}
        acoes = (
            ("Subciclo", "subciclo"),
            ("Ciclo", "ciclo"),
            ("Macro", "macro"),
            ("Iniciar", "iniciar"),
            ("Pausar", "pausar"),
            ("Reset", "reset"),
        )
        for coluna, (rotulo, acao) in enumerate(acoes):
            botao = ctk.CTkButton(
                self, text=rotulo, width=88, height=30,
                fg_color="#255c85" if acao not in ("reset", "pausar") else "#48576b",
                hover_color="#3075a6" if acao not in ("reset", "pausar") else "#65768b",
                command=lambda a=acao: self._executar(a),
            )
            botao.grid(row=0, column=coluna, padx=(8 if coluna == 0 else 2, 2), pady=(7, 3))
            self._botoes[acao] = botao
        self.label_velocidade = ctk.CTkLabel(
            self, text="12 subciclos/s", font=ctk.CTkFont(size=11),
            text_color="#b2c3d8",
        )
        self.label_velocidade.grid(row=1, column=0, columnspan=2,
                                   sticky="w", padx=8, pady=(0, 5))
        self.slider_velocidade = ctk.CTkSlider(
            self, from_=1, to=60, number_of_steps=59,
            variable=self.tela.painel_controle.velocidade,
            command=self.tela.painel_controle.definir_velocidade,
            width=170,
        )
        self.slider_velocidade.grid(row=1, column=2, columnspan=2,
                                    padx=5, pady=(0, 7), sticky="ew")
        self.label_status = ctk.CTkLabel(
            self, text="Status: pronto", anchor="w",
            text_color="#b2c3d8", font=ctk.CTkFont(size=12),
        )
        self.label_status.grid(row=1, column=4, columnspan=2,
                               sticky="ew", padx=10, pady=(0, 7))
        self.atualizar_estado()

    def atualizar_estado(self):
        painel = self.tela.painel_controle
        disponivel = painel.cpu.programa_carregado and not painel.cpu.fim_programa
        executando = painel.execucao_ativa
        for acao in ("subciclo", "ciclo", "macro", "iniciar"):
            self._botoes[acao].configure(
                state="normal" if disponivel and not executando else "disabled"
            )
        self._botoes["pausar"].configure(state="normal" if executando else "disabled")
        self._botoes["iniciar"].configure(text="Retomar" if painel._ja_iniciou and
                                          not executando and disponivel else "Iniciar")
        self.label_velocidade.configure(text=f"{painel.velocidade.get()} subciclos/s")
        self.label_status.configure(text=painel.label_status.cget("text"))

    def _executar(self, acao):
        painel = self.tela.painel_controle
        if acao == "subciclo":
            painel.executar_subciclo()
        elif acao == "ciclo":
            painel.executar_ciclo()
        elif acao == "macro":
            painel.executar_macroinstrucao()
        elif acao == "iniciar":
            painel.iniciar_execucao()
        elif acao == "pausar":
            painel.pausar_execucao()
        elif acao == "reset":
            painel.reset()
        self.atualizar_estado()


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

        self.simulador = TelaSimulador(aba_simulador, cpu, self._atualizar_graficos)
        self.simulador.pack(fill="both", expand=True)
        self.simulador._atualizar_status = self._atualizar_barras
        self.painel_registradores = self.simulador.painel_registradores
        self.painel_estado = self.simulador.painel_estado
        self.painel_codigo = self.simulador.painel_codigo
        self.painel_controle = self.simulador.painel_controle
        self.painel_memoria = self.simulador.painel_memoria

        aba_datapath.grid_columnconfigure(0, weight=1)
        aba_datapath.grid_rowconfigure(0, weight=1)
        self.painel_datapath = PainelDatapath(aba_datapath, cpu)
        self.painel_datapath.grid(row=0, column=0, sticky="nsew")
        self.barra_datapath = BarraExecucao(aba_datapath, self)
        self.barra_datapath.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))

        aba_microprograma.grid_columnconfigure(0, weight=1)
        aba_microprograma.grid_rowconfigure(0, weight=1)
        self.painel_microprograma = PainelMicroprograma(aba_microprograma, cpu)
        self.painel_microprograma.grid(row=0, column=0, sticky="nsew")
        self.barra_microprograma = BarraExecucao(aba_microprograma, self)
        self.barra_microprograma.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))

        aba_cache.grid_columnconfigure(0, weight=1)
        aba_cache.grid_rowconfigure(0, weight=1)
        self.painel_cache = PainelCache(aba_cache, cpu)
        self.painel_cache.grid(row=0, column=0, sticky="nsew")
        self.barra_cache = BarraExecucao(aba_cache, self)
        self.barra_cache.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))

        aba_ram.grid_columnconfigure(0, weight=1)
        aba_ram.grid_rowconfigure(0, weight=1)
        self.painel_memoria_completa = PainelMemoria(aba_ram, cpu=cpu)
        self.painel_memoria_completa.grid(row=0, column=0, sticky="nsew")
        self.barra_memoria = BarraExecucao(aba_ram, self)
        self.barra_memoria.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))
        self.atualizar()

    def _barras(self):
        return (self.barra_datapath, self.barra_microprograma,
                self.barra_cache, self.barra_memoria)

    def _atualizar_barras(self, _texto=None):
        for barra in self._barras():
            barra.atualizar_estado()

    def _atualizar_graficos(self):
        self.painel_datapath.atualizar()
        self.painel_microprograma.atualizar()
        self.painel_cache.atualizar()
        self.painel_memoria_completa.atualizar()
        if hasattr(self, "barra_memoria"):
            self._atualizar_barras()

    def atualizar(self):
        self.simulador.atualizar()
