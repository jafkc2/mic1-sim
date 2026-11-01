class Registradores:
    def __init__(self):
        self.pc = 0
        self.ac = 0
        self.sp = 0
        # falta adicionar o resto dos registradores

    def get_registradores(self):
        return {
            "PC": self.pc,
            "AC": self.ac,
            "SP": self.sp
        }