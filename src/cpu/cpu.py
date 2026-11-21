from cpu.datapath import DataPath
import montador
from memory import ControladorMemoria


class CPU:
    def __init__(self, programa=None):
        self.data_path = DataPath()
        self.memoria = ControladorMemoria()
        self.ciclos_executados = 0

        if programa is not None:
            self.carregar_programa(programa)

    def executar_subciclo(self):
        pass

    def executar_ciclo(self):
        pass

    def carregar_programa(self, programa: str | None):
        if programa is None:
            return

        palavras = montador.montar(programa)
        self.memoria.carregar_programa(palavras)
        self.data_path = DataPath()
        self.ciclos_executados = 0

    def reset(self):
        self.memoria.reset()
        self.data_path = DataPath()
        self.ciclos_executados = 0
