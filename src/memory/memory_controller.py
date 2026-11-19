from __future__ import annotations

from dataclasses import dataclass

from .config import CICLOS_ACESSO_RAM, CICLOS_CONSULTA_CACHE
from .cache import CacheMapeamentoDireto, DetalhesCache
from .ram import MemoriaRAM


@dataclass(frozen=True)
class ResultadoAcesso:
    cache: str
    operacao: str
    endereco: int
    valor: int
    hit: bool
    indice: int
    tag: int
    deslocamento: int
    inicio_bloco: int
    houve_substituicao: bool
    bloco_removido: int | None
    ciclos: int
    icache_invalidada: bool = False

    @property
    def miss(self) -> bool:
        return not self.hit


class ControladorMemoria:
    def __init__(self) -> None:
        self.ram = MemoriaRAM()
        self.icache = CacheMapeamentoDireto(self.ram, nome="I", somente_leitura=True)
        self.dcache = CacheMapeamentoDireto(self.ram, nome="D")
        self.ciclos_cache = CICLOS_CONSULTA_CACHE
        self.ciclos_ram = CICLOS_ACESSO_RAM
        self.ultimo_acesso: ResultadoAcesso | None = None

    def _resultado(self, tipo_cache: str, operacao: str, valor: int,
                   d: DetalhesCache, ciclos: int,
                   icache_invalidada: bool = False) -> ResultadoAcesso:
        r = ResultadoAcesso(
            cache=tipo_cache, operacao=operacao, endereco=d.endereco, valor=valor,
            hit=d.hit, indice=d.indice, tag=d.tag, deslocamento=d.deslocamento,
            inicio_bloco=d.inicio_bloco, houve_substituicao=d.substituiu,
            bloco_removido=d.bloco_removido, ciclos=ciclos,
            icache_invalidada=icache_invalidada,
        )
        self.ultimo_acesso = r
        return r

    def ler_instrucao(self, endereco: int) -> ResultadoAcesso:
        valor, d = self.icache.ler(endereco)
        ciclos = self.ciclos_cache + (0 if d.hit else self.ciclos_ram)
        return self._resultado("I", "leitura", valor, d, ciclos)

    def ler_dado(self, endereco: int) -> ResultadoAcesso:
        valor, d = self.dcache.ler(endereco)
        ciclos = self.ciclos_cache + (0 if d.hit else self.ciclos_ram)
        return self._resultado("D", "leitura", valor, d, ciclos)

    def escrever_dado(self, endereco: int, valor: int) -> ResultadoAcesso:
        d = self.dcache.escrever(endereco, valor)
        ciclos = self.ciclos_cache + self.ciclos_ram
        if not d.hit:
            ciclos += self.ciclos_ram
        invalidou = self.icache.invalidar_bloco(endereco)
        return self._resultado("D", "escrita", self.ram.ler(endereco), d,
                               ciclos, icache_invalidada=invalidou)

    def carregar_programa(self, palavras: list[int], endereco_inicial: int = 0,
                         *, limpar_ram: bool = True) -> None:
        self.ram._validar_endereco(endereco_inicial)
        valores = [self.ram._normalizar_palavra(v) for v in palavras]
        if endereco_inicial + len(valores) > self.ram.tamanho:
            raise ValueError("Programa ultrapassa os limites da RAM.")
        if limpar_ram:
            self.ram.limpar()
        self.ram.carregar(valores, endereco_inicial)
        self.limpar_caches()

    def limpar_caches(self) -> None:
        self.icache.limpar()
        self.dcache.limpar()
        self.ultimo_acesso = None

    def reset(self) -> None:
        self.ram.limpar()
        self.limpar_caches()