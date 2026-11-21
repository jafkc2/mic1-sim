import customtkinter as ctk


class PainelRegistradores(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.cpu = master.cpu
        self.labels = {}

        ctk.CTkLabel(self, text="Registradores", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=2, pady=(10, 5), sticky="w"
        )
        self.atualizar()

    def atualizar(self):
        registradores = self.cpu.data_path.get_registradores()
        linha = 1

        for nome, valor in registradores.items():
            coluna = 0 if linha % 2 == 1 else 1
            linha_grade = ((linha - 1) // 2) + 1
            chave = "{}-{}".format(coluna, linha_grade)

            if chave not in self.labels:
                label = ctk.CTkLabel(self, text="{}: {}".format(nome, valor), anchor="w")
                label.grid(row=linha_grade, column=coluna, padx=10, pady=3, sticky="w")
                self.labels[chave] = (label, nome)
            else:
                label, _ = self.labels[chave]
                label.configure(text="{}: {}".format(nome, valor))

            linha += 1
