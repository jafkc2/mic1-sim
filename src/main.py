from cpu.cpu import CPU
from app import App

def main():
    cpu = CPU()
    app = App(cpu)
    
    app.mainloop()

if __name__ == "__main__":
    main()
