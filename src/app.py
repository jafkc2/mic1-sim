import customtkinter as ctk
from cpu.cpu import CPU
from telas.tela_principal import TelaPrincipal


class App(ctk.CTk):
    def __init__(self, cpu):
        ctk.set_appearance_mode("dark")

        super().__init__()
        self.cpu : CPU = cpu
        self.title("MIC-1 Sim")
        self.geometry("1000x650")
        self.resizable(True, True)
        self.tela_principal = TelaPrincipal(self, cpu)
        self.tela_principal.pack(fill="both", expand=True)