class DataPath:
    def __init__(self):
        self.pc = 0
        self.ac = 0
        self.sp = 0
        self.ir = 0
        self.tir = 0

        self.c0 = 0
        self.cmais1 = 0
        self.cmenos1 = 0
        self.amask = 0
        self.smask = 0

        self.mbr = 0
        self.mar = 0 
        self.mpc = 0
        self.mdr = 0

        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.f = 0

    def get_registradores(self):
        return {
            "PC": self.pc,
            "AC": self.ac,
            "SP": self.sp,
            "IR": self.ir,
            "TIR": self.tir,
            "0": self.c0,
            "+1": self.cmais1,
            "-1": self.cmenos1,
            "AMASK": self.amask,
            "SMASK": self.smask,
            "MBR": self.mbr,
            "MAR": self.mar,
            "MPC": self.mpc,
            "MDR": self.mdr,
            "A": self.a,
            "B": self.b,
            "C": self.c,
            "D": self.d,
            "E": self.e,
            "F": self.f
        }