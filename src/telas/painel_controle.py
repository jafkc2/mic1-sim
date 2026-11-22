import customtkinter as ctk

from cpu.cpu import CPU


class PainelControle(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.cpu : CPU = master.cpu

        ctk.CTkLabel(self, text="Controles", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, pady=(10, 5), sticky="w"
        )
        self.botao_subciclo = ctk.CTkButton(
            self, text="Executar subciclo", command=self.executar_subciclo
        )
        self.botao_subciclo.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.botao_ciclo = ctk.CTkButton(
            self, text="Executar ciclo", command=self.executar_ciclo
        )
        self.botao_ciclo.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.botao_programa = ctk.CTkButton(
            self, text="Executar programa", command=self.executar_programa
        )
        self.botao_programa.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.botao_reset = ctk.CTkButton(
            self, text="Reset", command=self.reset
        )
        self.botao_reset.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        self.label_status = ctk.CTkLabel(self, text="Status: pronto")
        self.label_status.grid(row=5, column=0, padx=10, pady=5, sticky="w")

    def executar_subciclo(self):
        try:
            executou = self.cpu.executar_subciclo()
            texto = "subciclo executado" if executou else "fim do programa"
            self.label_status.configure(text="Status: " + texto)
            self.master.atualizar()
        except NotImplementedError as erro:
            self.label_status.configure(text="Status: {}".format(erro))
        except Exception as erro:
            self.label_status.configure(text="Erro: {}".format(erro))

    def executar_ciclo(self):
        try:
            executou = self.cpu.executar_ciclo()
            texto = "ciclo executado" if executou else "fim do programa"
            self.label_status.configure(text="Status: " + texto)
            self.master.atualizar()
        except NotImplementedError as erro:
            self.label_status.configure(text="Status: {}".format(erro))
        except Exception as erro:
            self.label_status.configure(text="Erro: {}".format(erro))

    def executar_programa(self):
        if hasattr(self.cpu, "executar_programa"):
            try:
                motivo = self.cpu.executar_programa()
                texto = {
                    "fim_programa": "programa concluido",
                    "limite_instrucoes": "limite de instrucoes atingido",
                    "limite_ciclos": "limite de ciclos atingido",
                }[motivo]
                self.label_status.configure(text="Status: " + texto)
                self.master.atualizar()
            except Exception as erro:
                self.label_status.configure(text="Erro: {}".format(erro))
        else:
            self.label_status.configure(text="Status: execucao completa ainda nao disponivel")

    def reset(self):
        try:
            self.cpu.reset()
            if self.cpu.programa_carregado:
                self.label_status.configure(text="Status: programa reiniciado")
                self.master.painel_codigo.label_status.configure(text="Status: programa carregado")
            else:
                self.label_status.configure(text="Status: CPU reiniciada")
                self.master.painel_codigo.label_status.configure(text="Status: aguardando")
            self.master.atualizar()
        except Exception as erro:
            self.label_status.configure(text="Erro: {}".format(erro))
