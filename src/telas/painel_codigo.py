import customtkinter as ctk

from cpu.cpu import CPU


class PainelCodigo(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.cpu : CPU = master.cpu

        ctk.CTkLabel(self, text="Programa Assembly", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=2, pady=(10, 5), sticky="w"
        )
        self.texto_codigo = ctk.CTkTextbox(self, width=520, height=220)
        self.texto_codigo.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.botao_carregar = ctk.CTkButton(
            self,
            text="Carregar programa",
            command=self.carregar_programa,
        )
        self.botao_carregar.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.label_status = ctk.CTkLabel(self, text="Status: aguardando")
        self.label_status.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def carregar_programa(self):
        codigo = self.texto_codigo.get("1.0", "end")
        self.master.painel_controle.pausar_execucao(silencioso=True)
        try:
            self.cpu.carregar_programa(codigo)
        except Exception as erro:
            if self.cpu.programa_carregado:
                self.label_status.configure(
                    text=f"Erro ao carregar: {erro}\nPrograma anterior continua carregado."
                )
                self.master.painel_controle.label_status.configure(
                    text="Status: programa anterior mantido"
                )
            else:
                self.label_status.configure(
                    text=f"Erro ao carregar: {erro}\nNenhum programa carregado."
                )
                self.master.painel_controle.label_status.configure(
                    text="Status: nenhum programa carregado"
                )
            self.master.atualizar()
            return

        self.master.painel_controle._inicio_ciclos = 0
        self.master.painel_controle._inicio_instrucoes = 0
        self.master.painel_controle._ja_iniciou = False
        self.label_status.configure(text="Status: programa carregado")
        self.master.painel_controle.label_status.configure(text="Status: pronto")
        self.master.atualizar()
