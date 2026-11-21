import customtkinter as ctk

from cpu.cpu import CPU


class PainelMemoria(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.cpu : CPU = master.cpu

        ctk.CTkLabel(self, text="Memoria RAM", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, pady=(10, 5), sticky="w"
        )
        self.texto_memoria = ctk.CTkTextbox(self, width=430, height=220)
        self.texto_memoria.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.atualizar()

    def atualizar(self):
        palavras = self.cpu.memoria.ram.visualizar(0, 16)
        linhas = []
        for endereco, valor in palavras:
            linhas.append("0x{:04X}: {:016b}".format(endereco, valor))

        self.texto_memoria.configure(state="normal")
        self.texto_memoria.delete("1.0", "end")
        self.texto_memoria.insert("1.0", "\n".join(linhas))
        self.texto_memoria.configure(state="disabled")
