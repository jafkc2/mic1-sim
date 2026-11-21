from __future__ import annotations

from dataclasses import asdict, dataclass, replace

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


@dataclass(frozen=True)
class RequisicaoMemoria:
    cache: str
    operacao: str
    endereco: int
    valor: int | None
    hit: bool
    ciclos_totais: int
    ciclos_restantes: int


@dataclass
class EstatisticasMemoria:
    leituras_instrucao: int = 0
    leituras_dados: int = 0
    escritas_dados: int = 0
    ciclos_leituras_instrucao: int = 0
    ciclos_leituras_dados: int = 0
    ciclos_escritas_dados: int = 0
    acessos_ram_leitura: int = 0
    acessos_ram_escrita: int = 0
    palavras_lidas_ram: int = 0
    ciclos_espera_cpu: int = 0

    @property
    def acessos(self) -> int:
        return self.leituras_instrucao + self.leituras_dados + self.escritas_dados

    @property
    def acessos_ram(self) -> int:
        return self.acessos_ram_leitura + self.acessos_ram_escrita

    @property
    def ciclos_memoria(self) -> int:
        return (self.ciclos_leituras_instrucao + self.ciclos_leituras_dados
                + self.ciclos_escritas_dados)

    @property
    def amat_instrucao(self) -> float:
        return (self.ciclos_leituras_instrucao / self.leituras_instrucao
                if self.leituras_instrucao else 0.0)

    @property
    def amat_dados(self) -> float:
        return (self.ciclos_leituras_dados / self.leituras_dados
                if self.leituras_dados else 0.0)

    @property
    def amat(self) -> float:
        leituras = self.leituras_instrucao + self.leituras_dados
        return ((self.ciclos_leituras_instrucao + self.ciclos_leituras_dados)
                / leituras if leituras else 0.0)

    @property
    def latencia_media_escrita(self) -> float:
        return (self.ciclos_escritas_dados / self.escritas_dados
                if self.escritas_dados else 0.0)

    @property
    def latencia_media(self) -> float:
        return self.ciclos_memoria / self.acessos if self.acessos else 0.0


class ControladorMemoria:
    def __init__(self) -> None:
        self.ram = MemoriaRAM()
        self.icache = CacheMapeamentoDireto(self.ram, nome="I", somente_leitura=True)
        self.dcache = CacheMapeamentoDireto(self.ram, nome="D")
        self.ciclos_cache = CICLOS_CONSULTA_CACHE
        self.ciclos_ram = CICLOS_ACESSO_RAM
        self.ultimo_acesso: ResultadoAcesso | None = None
        self._pendente: RequisicaoMemoria | None = None
        self._resultado_pronto: ResultadoAcesso | None = None
        self._sinal_em_aberto: str | None = None
        self._estatisticas = EstatisticasMemoria()

    @property
    def requisicao_pendente(self) -> RequisicaoMemoria | None:
        return self._pendente

    @property
    def ciclos_restantes(self) -> int:
        return self._pendente.ciclos_restantes if self._pendente else 0

    @property
    def estatisticas(self) -> EstatisticasMemoria:
        return replace(self._estatisticas)

    def get_estatisticas(self) -> dict[str, int | float]:
        e = self.estatisticas
        return {**asdict(e), "acessos": e.acessos, "acessos_ram": e.acessos_ram,
                "ciclos_memoria": e.ciclos_memoria, "amat": e.amat,
                "amat_instrucao": e.amat_instrucao, "amat_dados": e.amat_dados,
                "latencia_media_escrita": e.latencia_media_escrita,
                "latencia_media": e.latencia_media,
                "hits": self.icache.estatisticas.hits + self.dcache.estatisticas.hits,
                "misses": self.icache.estatisticas.misses + self.dcache.estatisticas.misses}

    def _registrar_acesso(self, r: ResultadoAcesso) -> None:
        e = self._estatisticas
        if r.cache == "I":
            e.leituras_instrucao += 1
            e.ciclos_leituras_instrucao += r.ciclos
        elif r.operacao == "leitura":
            e.leituras_dados += 1
            e.ciclos_leituras_dados += r.ciclos
        else:
            e.escritas_dados += 1
            e.ciclos_escritas_dados += r.ciclos
            e.acessos_ram_escrita += 1
        if r.miss:
            e.acessos_ram_leitura += 1
            cache = self.icache if r.cache == "I" else self.dcache
            e.palavras_lidas_ram += cache.palavras_por_bloco

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
        self._registrar_acesso(r)
        return r

    def _latencia(self, operacao: str, hit: bool) -> int:
        return (self.ciclos_cache + (0 if hit else self.ciclos_ram)
                + (self.ciclos_ram if operacao == "escrita" else 0))

    def _executar_acesso(self, tipo_cache: str, operacao: str, endereco: int,
                         valor: int | None = None) -> ResultadoAcesso:
        cache = self.icache if tipo_cache == "I" else self.dcache
        if operacao == "leitura":
            dado, d = cache.ler(endereco)
            return self._resultado(tipo_cache, operacao, dado, d,
                                   self._latencia(operacao, d.hit))
        dado = self.ram._normalizar_palavra(valor)
        d = cache.escrever(endereco, dado)
        invalidou = self.icache.invalidar_bloco(endereco)
        return self._resultado(tipo_cache, operacao, dado, d,
                               self._latencia(operacao, d.hit),
                               icache_invalidada=invalidou)

    def _exigir_livre(self) -> None:
        if (self._pendente is not None or self._resultado_pronto is not None
                or self._sinal_em_aberto is not None):
            raise RuntimeError("Existe uma requisicao de memoria nao finalizada.")

    def ler_instrucao(self, endereco: int) -> ResultadoAcesso:
        self._exigir_livre()
        return self._executar_acesso("I", "leitura", endereco)

    def ler_dado(self, endereco: int) -> ResultadoAcesso:
        self._exigir_livre()
        return self._executar_acesso("D", "leitura", endereco)

    def escrever_dado(self, endereco: int, valor: int) -> ResultadoAcesso:
        self._exigir_livre()
        return self._executar_acesso("D", "escrita", endereco, valor)

    def _consultar_hit(self, tipo_cache: str, endereco: int) -> bool:
        cache = self.icache if tipo_cache == "I" else self.dcache
        partes = cache.decompor_endereco(endereco)
        linha = cache.linhas[partes["indice"]]
        return linha.valido and linha.tag == partes["tag"]

    def _iniciar(self, tipo_cache: str, operacao: str, endereco: int,
                 valor: int | None = None) -> RequisicaoMemoria:
        self._exigir_livre()
        self.ram._validar_endereco(endereco)
        if operacao == "escrita":
            valor = self.ram._normalizar_palavra(valor)
        hit = self._consultar_hit(tipo_cache, endereco)
        ciclos = self._latencia(operacao, hit)
        self._pendente = RequisicaoMemoria(tipo_cache, operacao, endereco, valor,
                                          hit, ciclos, ciclos)
        return self._pendente

    def iniciar_leitura(self, endereco: int, *, instrucao: bool = False) -> RequisicaoMemoria:
        if type(instrucao) is not bool:
            raise TypeError("instrucao deve ser booleano.")
        return self._iniciar("I" if instrucao else "D", "leitura", endereco)

    def iniciar_escrita(self, endereco: int, valor: int) -> RequisicaoMemoria:
        return self._iniciar("D", "escrita", endereco, valor)

    def memoria_ocupada(self) -> bool:
        return self._pendente is not None

    def resultado_disponivel(self) -> bool:
        return self._resultado_pronto is not None and self._sinal_em_aberto is None

    def avancar_ciclo(self, *, espera_cpu: bool = False) -> bool:
        if type(espera_cpu) is not bool:
            raise TypeError("espera_cpu deve ser booleano.")
        r = self._pendente
        if r is None:
            return False
        if r.ciclos_restantes == 1:
            if self._consultar_hit(r.cache, r.endereco) != r.hit:
                raise RuntimeError("Cache alterada durante uma requisicao de memoria.")
            self._resultado_pronto = self._executar_acesso(r.cache, r.operacao,
                                                          r.endereco, r.valor)
            self._pendente = None
        else:
            self._pendente = replace(r, ciclos_restantes=r.ciclos_restantes - 1)
        if espera_cpu:
            self._estatisticas.ciclos_espera_cpu += 1
        return self._pendente is None

    def obter_resultado(self) -> ResultadoAcesso | None:
        if not self.resultado_disponivel():
            return None
        r = self._resultado_pronto
        self._resultado_pronto = None
        return r

    def processar_sinais(self, rd: int, wr: int, endereco: int | None = None,
                         valor: int | None = None, *, instrucao: bool = False) -> None:
        if (not isinstance(rd, int) or rd not in (0, 1)
                or not isinstance(wr, int) or wr not in (0, 1)):
            raise ValueError("RD e WR devem ser 0 ou 1.")
        if rd and wr:
            raise ValueError("RD e WR nao podem ser ativados simultaneamente neste modelo.")
        sinal = "leitura" if rd else "escrita" if wr else None
        if self._sinal_em_aberto is not None:
            if sinal != self._sinal_em_aberto:
                raise RuntimeError("Segundo sinal RD/WR esperado para concluir a requisicao.")
            self._sinal_em_aberto = None
            return
        if sinal is None:
            self._exigir_livre()
            return
        if sinal == "leitura":
            self.iniciar_leitura(endereco, instrucao=instrucao)
        else:
            self.iniciar_escrita(endereco, valor)
        self._sinal_em_aberto = sinal

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
        self._pendente = None
        self._resultado_pronto = None
        self._sinal_em_aberto = None
        self._estatisticas = EstatisticasMemoria()

    def reset(self) -> None:
        self.ram.limpar()
        self.limpar_caches()
