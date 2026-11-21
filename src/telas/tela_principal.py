import customtkinter as ctk
from .painel_codigo import PainelCodigo
from .painel_controle import PainelControle
from .painel_estado_cpu import PainelEstadoCPU
from .painel_memoria import PainelMemoria
from .painel_registradores import PainelRegistradores


class TelaPrincipal(ctk.CTkFrame):
    def __init__(self, master, cpu):
        super().__init__(master)
        self.cpu = cpu

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.painel_registradores = PainelRegistradores(self)
        self.painel_registradores.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.painel_estado = PainelEstadoCPU(self)
        self.painel_estado.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.painel_codigo = PainelCodigo(self)
        self.painel_codigo.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.painel_controle = PainelControle(self)
        self.painel_controle.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.painel_memoria = PainelMemoria(self.painel_estado)
        self.painel_memoria.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.atualizar()

    def atualizar(self):
        self.painel_registradores.atualizar()
        self.painel_estado.atualizar()
        self.painel_memoria.atualizar()
