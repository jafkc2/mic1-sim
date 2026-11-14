from cpu.datapath import DataPath
import montador

class CPU:
    def __init__(self, programa=None):
        # subclasses
        self.data_path = DataPath()

        self.carregar_programa(programa)

    # n implementado ainda, precisamos das subclasses.
    def executar_subciclo(self):
        pass
    def executar_ciclo(self):
        pass
    def carregar_programa(self, programa):
        memoria = montador.montar(programa)
        pass
    
        

        