from cpu.cpu import CPU
from app import App

if __name__ == "__main__":
    cpu = CPU()
    app = App(cpu)
    
    app.mainloop()
