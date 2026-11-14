"""Execute da raiz: python examples/demo_memoria.py"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from memory import ControladorMemoria


def mostrar_evento(r):
    status = "HIT " if r.hit else "MISS"
    print(f"[{r.cache}] {r.operacao:7} end={r.endereco:4} "
          f"tag={r.tag} linha={r.indice} desloc={r.deslocamento} "
          f"{status} valor=0x{r.valor:04X} ciclos={r.ciclos}")
    if r.icache_invalidada:
        print("    (bloco correspondente da I-Cache invalidado)")


def main():
    controlador = ControladorMemoria()
    controlador.carregar_programa([0x7005, 0x1064, 0x7007, 0x2064, 0x1065])
    print("=== Busca de instrucoes: localidade espacial ===")
    mostrar_evento(controlador.ler_instrucao(0))
    mostrar_evento(controlador.ler_instrucao(1))
    mostrar_evento(controlador.ler_instrucao(4))

    print("\n=== Cache de dados: write-through + write-allocate ===")
    mostrar_evento(controlador.escrever_dado(100, 5))
    mostrar_evento(controlador.ler_dado(101))
    mostrar_evento(controlador.ler_dado(100))
    mostrar_evento(controlador.escrever_dado(101, 12))
    print("RAM[100] =", controlador.ram.ler(100))
    print("RAM[101] =", controlador.ram.ler(101))

    print("\n=== Linhas da D-Cache (dados para futuro ttk.Treeview) ===")
    for linha in controlador.dcache.visualizar():
        print(linha)

    stats = controlador.dcache.estatisticas
    print(f"\nD-Cache: {stats.hits} hits, {stats.misses} misses, taxa hit = {stats.taxa_hit:.0%}")


if __name__ == "__main__":
    main()
