"""Testes de RAM + caches, sem dependencias graficas."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from memory import CacheMapeamentoDireto, ControladorMemoria, MemoriaRAM


class TesteRAM(unittest.TestCase):
    def test_inicializacao_leitura_e_escrita(self):
        ram = MemoriaRAM()
        self.assertEqual(ram.tamanho, 4096)
        self.assertEqual(ram.ler(100), 0)
        ram.escrever(100, 12)
        self.assertEqual(ram.ler(100), 12)

    def test_mascara_de_16_bits(self):
        ram = MemoriaRAM()
        ram.escrever(42, -1)
        self.assertEqual(ram.ler(42), 0xFFFF)
        ram.escrever(42, 0x10005)
        self.assertEqual(ram.ler(42), 5)

    def test_limites_e_carga_atomica(self):
        ram = MemoriaRAM()
        for endereco in (-1, 4096):
            with self.assertRaises(ValueError):
                ram.ler(endereco)
        with self.assertRaises(ValueError):
            ram.carregar([10, 20], 4095)
        self.assertEqual(ram.ler(4095), 0)
        ram.carregar([0x7005, 0x1064])
        self.assertEqual(ram.visualizar(0, 2), [(0, 0x7005), (1, 0x1064)])


class TesteCache(unittest.TestCase):
    def setUp(self):
        self.ram = MemoriaRAM()
        self.controlador = ControladorMemoria(self.ram)

    def test_mapeamento(self):
        partes = self.controlador.dcache.decompor_endereco(21)
        self.assertEqual(partes, {"tag": 1, "indice": 1,
                                  "deslocamento": 1, "inicio_bloco": 20})

    def test_hit_localidade_espacial(self):
        self.ram.carregar([10, 20, 30, 40], 20)
        r1 = self.controlador.ler_dado(21)
        r2 = self.controlador.ler_dado(20)
        self.assertFalse(r1.hit)
        self.assertTrue(r2.hit)
        self.assertEqual((r1.valor, r2.valor), (20, 10))
        self.assertEqual((r1.ciclos, r2.ciclos), (11, 1))
        self.assertEqual(self.controlador.dcache.estatisticas.blocos_carregados, 1)

    def test_conflito_e_substituicao(self):
        r1 = self.controlador.ler_dado(2)   # bloco 0 -> linha 0
        r2 = self.controlador.ler_dado(18)  # bloco 4 -> linha 0
        r3 = self.controlador.ler_dado(2)   # volta ao bloco 0
        self.assertFalse(r1.hit)
        self.assertFalse(r2.hit)
        self.assertTrue(r2.houve_substituicao)
        self.assertEqual(r2.bloco_removido, 0)
        self.assertFalse(r3.hit)
        self.assertEqual(self.controlador.dcache.estatisticas.substituicoes, 2)

    def test_write_through_e_write_allocate(self):
        primeiro = self.controlador.escrever_dado(100, 0xABCD)
        segundo = self.controlador.escrever_dado(100, 22)
        leitura = self.controlador.ler_dado(100)
        self.assertFalse(primeiro.hit)
        self.assertEqual(primeiro.ciclos, 21)
        self.assertTrue(segundo.hit)
        self.assertEqual(segundo.ciclos, 11)
        self.assertTrue(leitura.hit)
        self.assertEqual(leitura.valor, 22)
        self.assertEqual(self.ram.ler(100), 22)

    def test_icache_somente_leitura(self):
        with self.assertRaises(PermissionError):
            self.controlador.icache.escrever(0, 4)

    def test_caches_separadas(self):
        self.controlador.ler_instrucao(0)
        self.assertEqual(self.controlador.icache.estatisticas.misses, 1)
        self.assertEqual(self.controlador.dcache.estatisticas.acessos, 0)
        self.controlador.ler_dado(0)
        self.assertEqual(self.controlador.dcache.estatisticas.misses, 1)

    def test_coerencia_instrucoes_modificadas(self):
        self.ram.escrever(20, 0x7005)
        self.assertEqual(self.controlador.ler_instrucao(20).valor, 0x7005)
        escrita = self.controlador.escrever_dado(20, 0x7009)
        self.assertTrue(escrita.icache_invalidada)
        nova_leitura = self.controlador.ler_instrucao(20)
        self.assertFalse(nova_leitura.hit)
        self.assertEqual(nova_leitura.valor, 0x7009)

    def test_carregamento_invalida_ambas_caches(self):
        self.controlador.ler_instrucao(0)
        self.controlador.ler_dado(0)
        self.controlador.carregar_programa([0x7005, 0x1064])
        self.assertEqual(self.ram.ler(0), 0x7005)
        self.assertEqual(self.controlador.icache.estatisticas.acessos, 0)
        self.assertEqual(self.controlador.dcache.estatisticas.acessos, 0)
        self.assertFalse(self.controlador.ler_instrucao(0).hit)

    def test_invalido_nao_altera_estatistica(self):
        with self.assertRaises(ValueError):
            self.controlador.ler_dado(4096)
        with self.assertRaises(TypeError):
            self.controlador.escrever_dado(10, "X")
        self.assertEqual(self.controlador.dcache.estatisticas.acessos, 0)

    def test_visualizar_devolve_copia(self):
        self.controlador.escrever_dado(100, 42)
        view = self.controlador.dcache.visualizar()
        view[1]["dados"][0] = 9999
        self.assertEqual(self.controlador.ler_dado(100).valor, 42)


if __name__ == "__main__":
    unittest.main()
