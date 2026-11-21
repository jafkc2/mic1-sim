import customtkinter as ctk


class App(ctk.CTk):
    def __init__(self, cpu):
        super().__init__()
        self.cpu = cpu
        self.title("MIC-1 Sim")
        self.geometry("854x480")
        self.resizable(False,  False)
        self.mostrar_registradores()

    def mostrar_registradores(self):
        registradores = self.cpu.data_path.get_registradores()
        for i, valor in registradores.items():
            ctk.CTkLabel(self, text=f"Registrador {i}: {valor}").pack()
            