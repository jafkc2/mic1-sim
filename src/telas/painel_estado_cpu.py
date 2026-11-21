import customtkinter as ctk

from cpu.cpu import CPU


class PainelEstadoCPU(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.cpu : CPU = master.cpu

        ctk.CTkLabel(self, text="Estado da CPU", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=2, pady=(10, 5), sticky="w"
        )
        self.label_flags = ctk.CTkLabel(self, text="Flags: N=0 Z=0")
        self.label_flags.grid(row=1, column=0, padx=10, pady=3, sticky="w")
        self.label_ciclos = ctk.CTkLabel(self, text="Ciclos executados: 0")
        self.label_ciclos.grid(row=2, column=0, padx=10, pady=3, sticky="w")
        self.label_ultimo_acesso = ctk.CTkLabel(self, text="Ultimo acesso: nenhum")
        self.label_ultimo_acesso.grid(row=3, column=0, padx=10, pady=3, sticky="w")
        self.atualizar()

    def atualizar(self):
        flags = self.cpu.data_path.get_flags()
        self.label_flags.configure(
            text="Flags: N={} Z={}".format("1" if flags["N"] else "0", "1" if flags["Z"] else "0")
        )
        ciclos = getattr(self.cpu, "ciclos_executados", 0)
        self.label_ciclos.configure(text="Ciclos executados: {}".format(ciclos))

        acesso = self.cpu.memoria.ultimo_acesso
        if acesso is None:
            texto = "Ultimo acesso: nenhum"
        else:
            texto = "Ultimo acesso: {} {} endereco={} valor={} ciclos={}".format(
                acesso.cache,
                acesso.operacao,
                acesso.endereco,
                acesso.valor,
                acesso.ciclos,
            )
        self.label_ultimo_acesso.configure(text=texto)
