"""Teste minimo de integracao do pacote memoria com a CPU existente."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from cpu.cpu import CPU


class TesteIntegracaoCPU(unittest.TestCase):
    def test_cpu_aceita_programa_ausente(self):
        cpu = CPU()
        self.assertEqual(cpu.ram.ler(0), 0)
        self.assertIs(cpu.memoria.ram, cpu.ram)

    def test_cpu_carrega_assembly_simples(self):
        cpu = CPU("LOCO 5\nSTOD 100")
        self.assertEqual(cpu.ram.ler(0), 0x7005)
        self.assertEqual(cpu.ram.ler(1), 0x1064)
        self.assertEqual(cpu.memoria.ler_instrucao(0).valor, 0x7005)


if __name__ == "__main__":
    unittest.main()
