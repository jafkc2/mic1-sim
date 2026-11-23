import customtkinter as ctk

from .cores import Paleta


class BarraExecucao(Paleta, ctk.CTkFrame):
    def __init__(self, master, tela):
        super().__init__(master, fg_color=self.PAINEL, corner_radius=7)
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
                self,
                text=rotulo,
                width=88,
                height=30,
                fg_color=self.BOTAO_AZUL if acao not in ("reset", "pausar") else self.BOTAO_NEUTRO,
                hover_color=self.BOTAO_AZUL_HOVER if acao not in ("reset", "pausar") else self.BOTAO_NEUTRO_HOVER,
                command=lambda acao=acao: self._executar(acao),
            )
            botao.grid(
                row=0,
                column=coluna,
                padx=(8 if coluna == 0 else 2, 2),
                pady=(7, 3),
            )
            self._botoes[acao] = botao
        self.label_status = ctk.CTkLabel(
            self,
            text="Status: pronto",
            anchor="w",
            text_color="#b2c3d8",
            font=ctk.CTkFont(size=12),
        )
        self.label_status.grid(
            row=0,
            column=6,
            sticky="ew",
            padx=10,
        )
        self.atualizar_estado()

    def atualizar_estado(self):
        painel = self.tela.painel_controle
        disponivel = painel.cpu.programa_carregado and not painel.cpu.fim_programa
        executando = painel.execucao_ativa
        for acao in ("subciclo", "ciclo", "macro", "iniciar"):
            estado = "normal" if disponivel and not executando else "disabled"
            self._botoes[acao].configure(state=estado)
        self._botoes["pausar"].configure(
            state="normal" if executando else "disabled"
        )
        iniciar = "Retomar" if (
            painel._ja_iniciou
            and not executando
            and disponivel
        ) else "Iniciar"
        self._botoes["iniciar"].configure(text=iniciar)
        self.label_status.configure(
            text=painel.label_status.cget("text")
        )

    def _executar(self, acao):
        painel = self.tela.painel_controle
        comandos = {
            "subciclo": painel.executar_subciclo,
            "ciclo": painel.executar_ciclo,
            "macro": painel.executar_macroinstrucao,
            "iniciar": painel.iniciar_execucao,
            "pausar": painel.pausar_execucao,
            "reset": painel.reset,
        }
        comandos[acao]()
        self.atualizar_estado()
