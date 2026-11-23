import customtkinter as ctk

from .codigo import PainelCodigo
from .controle import PainelControle
from .estado_cpu import PainelEstadoCPU
from .registradores import PainelRegistradores
from ..memoria import PainelMemoria

__all__ = [
    "AbaSimulador",
    "PainelCodigo",
    "PainelControle",
    "PainelEstadoCPU",
    "PainelRegistradores",
]


class AbaSimulador(ctk.CTkFrame):
    def __init__(self, master, cpu, atualizar_graficos):
        super().__init__(master, fg_color="transparent")
        self.cpu = cpu
        self.atualizar_graficos = atualizar_graficos
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=4)

        self.painel_registradores = PainelRegistradores(self)
        self.painel_registradores.grid(row=0, column=0, padx=7, pady=7, sticky="nsew")

        self.painel_estado = PainelEstadoCPU(self)
        self.painel_estado.grid(row=0, column=1, padx=7, pady=7, sticky="nsew")

        self.painel_codigo = PainelCodigo(self)
        self.painel_codigo.grid(row=1, column=0, padx=7, pady=7, sticky="nsew")

        self.painel_controle = PainelControle(self)
        self.painel_controle.grid(row=1, column=1, padx=7, pady=7, sticky="nsew")

        self.painel_memoria = PainelMemoria(self.painel_estado, compacto=True)
        self.painel_memoria.grid(
            row=2, column=0, columnspan=2,
            padx=8, pady=6, sticky="nsew",
        )

    def atualizar(self):
        self.painel_registradores.atualizar()
        self.painel_estado.atualizar()
        self.painel_memoria.atualizar()
        self.painel_controle.atualizar_botoes()
        self.atualizar_graficos()
