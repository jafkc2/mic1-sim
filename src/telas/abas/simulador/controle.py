import customtkinter as ctk

from cpu.cpu import CPU
from ...cores import Paleta


class PainelControle(Paleta, ctk.CTkFrame):
    MAX_INSTRUCOES = 1000
    MAX_CICLOS = 100000

    def __init__(self, master):
        super().__init__(master)
        self.cpu: CPU = master.cpu
        self.velocidade = ctk.IntVar(value=12)
        self.execucao_ativa = False
        self._apos_id = None
        self._inicio_instrucoes = 0
        self._inicio_ciclos = 0
        self._ja_iniciou = False
        self.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self, text="Controles de execução",
                     font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=(9, 3), sticky="w"
        )
        self.botao_subciclo = ctk.CTkButton(
            self, text="Executar subciclo", command=self.executar_subciclo,
        )
        self.botao_subciclo.grid(row=1, column=0, padx=(10, 4), pady=3, sticky="ew")
        self.botao_ciclo = ctk.CTkButton(
            self, text="Executar ciclo", command=self.executar_ciclo,
        )
        self.botao_ciclo.grid(row=1, column=1, padx=(4, 10), pady=3, sticky="ew")
        self.botao_macro = ctk.CTkButton(
            self, text="Macroinstrução", command=self.executar_macroinstrucao,
        )
        self.botao_macro.grid(row=2, column=0, padx=(10, 4), pady=3, sticky="ew")
        self.botao_programa = ctk.CTkButton(
            self, text="Iniciar execução", command=self.iniciar_execucao,
        )
        self.botao_programa.grid(row=2, column=1, padx=(4, 10), pady=3, sticky="ew")
        self.botao_pausar = ctk.CTkButton(
            self, text="Pausar", command=self.pausar_execucao,
            fg_color=self.BOTAO_NEUTRO, hover_color=self.BOTAO_NEUTRO_HOVER,
        )
        self.botao_pausar.grid(row=3, column=0, padx=(10, 4), pady=3, sticky="ew")
        self.botao_reset = ctk.CTkButton(
            self, text="Reset", command=self.reset,
            fg_color=self.BOTAO_NEUTRO, hover_color=self.BOTAO_NEUTRO_HOVER,
        )
        self.botao_reset.grid(row=3, column=1, padx=(4, 10), pady=3, sticky="ew")
        self.label_velocidade = ctk.CTkLabel(self, text="Velocidade: 12 subciclos/s")
        self.label_velocidade.grid(row=4, column=0, columnspan=2, padx=10, pady=(4, 0), sticky="w")
        self.controle_velocidade = ctk.CTkSlider(
            self, from_=1, to=60, number_of_steps=59,
            variable=self.velocidade, command=self.definir_velocidade,
        )
        self.controle_velocidade.grid(row=5, column=0, columnspan=2,
                                     padx=14, pady=(1, 5), sticky="ew")
        self.label_status = ctk.CTkLabel(self, text="Status: pronto", anchor="w")
        self.label_status.grid(row=6, column=0, columnspan=2,
                               padx=10, pady=(1, 7), sticky="ew")
        self.atualizar_botoes()

    def _status(self, texto):
        self.label_status.configure(text="Status: " + texto)
        if hasattr(self.master, "_atualizar_status"):
            self.master._atualizar_status()

    def _notificar(self):
        self.master.atualizar()

    def atualizar_botoes(self):
        disponivel = self.cpu.programa_carregado and not self.cpu.fim_programa
        passo = "normal" if disponivel and not self.execucao_ativa else "disabled"
        for botao in (self.botao_subciclo, self.botao_ciclo, self.botao_macro):
            botao.configure(state=passo)
        self.botao_programa.configure(
            state="normal" if disponivel and not self.execucao_ativa else "disabled",
            text="Retomar execução" if self._ja_iniciou and not self.execucao_ativa
            and disponivel else "Iniciar execução",
        )
        self.botao_pausar.configure(state="normal" if self.execucao_ativa else "disabled")

    def definir_velocidade(self, _valor=None):
        self.label_velocidade.configure(
            text=f"Velocidade: {self.velocidade.get()} subciclos/s"
        )
        if hasattr(self.master, "_atualizar_status"):
            self.master._atualizar_status()

    def pausar_execucao(self, silencioso=False):
        estava_ativa = self.execucao_ativa
        self.execucao_ativa = False
        if self._apos_id is not None:
            try:
                self.after_cancel(self._apos_id)
            except ValueError:
                pass
            self._apos_id = None
        if estava_ativa and not silencioso:
            self._status("execução pausada")
        self.atualizar_botoes()
        if estava_ativa and not silencioso:
            self._notificar()

    def _agendar(self):
        if self.execucao_ativa:
            intervalo = max(15, int(1000 / self.velocidade.get()))
            self._apos_id = self.after(intervalo, self._passo_automatico)

    def iniciar_execucao(self):
        if self.execucao_ativa:
            return
        if not self.cpu.programa_carregado:
            self._status("carregue um programa antes de executar")
            return
        if self.cpu.fim_programa:
            self._status("programa concluído; utilize Reset para reexecutar")
            self.atualizar_botoes()
            return
        self._inicio_instrucoes = self.cpu.instrucoes_executadas
        self._inicio_ciclos = self.cpu.ciclos_executados
        self._ja_iniciou = True
        self.execucao_ativa = True
        self._status("execução contínua iniciada")
        self.atualizar_botoes()
        self._agendar()

    def _passo_automatico(self):
        self._apos_id = None
        if not self.execucao_ativa:
            return
        try:
            if self.cpu.fim_programa:
                self.pausar_execucao(silencioso=True)
                self._status("programa concluído")
            elif self.cpu.instrucoes_executadas - self._inicio_instrucoes >= self.MAX_INSTRUCOES:
                self.pausar_execucao(silencioso=True)
                self.cpu.motivo_parada = "limite_instrucoes"
                self._status("limite de instruções atingido")
            elif self.cpu.ciclos_executados - self._inicio_ciclos >= self.MAX_CICLOS:
                self.pausar_execucao(silencioso=True)
                self.cpu.motivo_parada = "limite_ciclos"
                self._status("limite de ciclos atingido")
            else:
                executou = self.cpu.executar_subciclo()
                if not executou or self.cpu.fim_programa:
                    self.pausar_execucao(silencioso=True)
                    self._status("programa concluído")
                else:
                    self._status("executando continuamente")
            self.atualizar_botoes()
            self._notificar()
        except Exception as erro:
            self.pausar_execucao(silencioso=True)
            self._status(f"Erro: {erro}")
            self._notificar()
        if self.execucao_ativa:
            self._agendar()

    def executar_subciclo(self):
        self.pausar_execucao(silencioso=True)
        try:
            executou = self.cpu.executar_subciclo()
            self._status("subciclo executado" if executou else "fim do programa")
            self._notificar()
        except Exception as erro:
            self._status(f"Erro: {erro}")
        self.atualizar_botoes()

    def executar_ciclo(self):
        self.pausar_execucao(silencioso=True)
        try:
            executou = self.cpu.executar_ciclo()
            self._status("ciclo executado" if executou else "fim do programa")
            self._notificar()
        except Exception as erro:
            self._status(f"Erro: {erro}")
        self.atualizar_botoes()

    def executar_macroinstrucao(self):
        self.pausar_execucao(silencioso=True)
        try:
            executou = self.cpu.executar_macroinstrucao()
            self._status("macroinstrução executada" if executou else
                         "fim do programa ou limite de ciclos")
            self._notificar()
        except Exception as erro:
            self._status(f"Erro: {erro}")
        self.atualizar_botoes()

    def executar_programa(self):
        self.pausar_execucao(silencioso=True)
        try:
            motivo = self.cpu.executar_programa()
            texto = {
                "fim_programa": "programa concluído",
                "limite_instrucoes": "limite de instruções atingido",
                "limite_ciclos": "limite de ciclos atingido",
            }[motivo]
            self._status(texto)
            self._notificar()
        except Exception as erro:
            self._status(f"Erro: {erro}")
        self.atualizar_botoes()

    def reset(self):
        self.pausar_execucao(silencioso=True)
        self._inicio_ciclos = 0
        self._inicio_instrucoes = 0
        self._ja_iniciou = False
        try:
            self.cpu.reset()
            if self.cpu.programa_carregado:
                self._status("programa reiniciado")
                self.master.painel_codigo.label_status.configure(
                    text="Status: programa carregado"
                )
            else:
                self._status("CPU reiniciada")
                self.master.painel_codigo.label_status.configure(text="Status: aguardando")
            self.atualizar_botoes()
            self._notificar()
        except Exception as erro:
            self._status(f"Erro: {erro}")

    def destroy(self):
        self.pausar_execucao(silencioso=True)
        super().destroy()
