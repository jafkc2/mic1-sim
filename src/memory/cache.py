# mapeamento direto

from __future__ import annotations

from dataclasses import dataclass, field

from .config import LINHAS_CACHE, PALAVRAS_POR_BLOCO
from .ram import MemoriaRAM


@dataclass
class LinhaCache:
    valido: bool = False
    tag: int = 0
    dados: list[int] = field(default_factory=list)


@dataclass
class EstatisticasCache:
    leituras: int = 0
    escritas: int = 0
    hits: int = 0
    misses: int = 0
    substituicoes: int = 0
    blocos_carregados: int = 0

    @property
    def acessos(self) -> int:
        return self.leituras + self.escritas

    @property
    def taxa_hit(self) -> float:
        return self.hits / self.acessos if self.acessos else 0.0

    @property
    def taxa_miss(self) -> float:
        return self.misses / self.acessos if self.acessos else 0.0


@dataclass(frozen=True)
class DetalhesCache:
    endereco: int
    indice: int
    tag: int
    deslocamento: int
    inicio_bloco: int
    hit: bool
    substituiu: bool
    bloco_removido: int | None


class CacheMapeamentoDireto:
    def __init__(
        self,
        ram: MemoriaRAM,
        *,
        nome: str,
        linhas: int = LINHAS_CACHE,
        palavras_por_bloco: int = PALAVRAS_POR_BLOCO,
        somente_leitura: bool = False,
    ) -> None:
        for valor, rotulo in ((linhas, "linhas"), (palavras_por_bloco, "palavras_por_bloco")):
            if type(valor) is not int or valor <= 0 or (valor & (valor - 1)) != 0:
                raise ValueError(f"{rotulo} deve ser potencia de 2 positiva.")
        if ram.tamanho % palavras_por_bloco != 0:
            raise ValueError("Tamanho do bloco deve dividir o tamanho da RAM.")
        self.ram = ram
        self.nome = nome
        self.quantidade_linhas = linhas
        self.palavras_por_bloco = palavras_por_bloco
        self.somente_leitura = somente_leitura
        self.linhas = [LinhaCache(dados=[0] * palavras_por_bloco) for _ in range(linhas)]
        self.estatisticas = EstatisticasCache()

    def _partes(self, endereco: int) -> tuple[int, int, int, int]:
        self.ram._validar_endereco(endereco)
        numero_bloco = endereco // self.palavras_por_bloco
        indice = numero_bloco % self.quantidade_linhas
        tag = numero_bloco // self.quantidade_linhas
        deslocamento = endereco % self.palavras_por_bloco
        inicio_bloco = numero_bloco * self.palavras_por_bloco
        return indice, tag, deslocamento, inicio_bloco

    def decompor_endereco(self, endereco: int) -> dict[str, int]:
        indice, tag, deslocamento, inicio_bloco = self._partes(endereco)
        return {"tag": tag, "indice": indice, "deslocamento": deslocamento,
                "inicio_bloco": inicio_bloco}


    #VER SE ALGUM ELEMENTO ESTA NA CHACHE
    def _localizar(self, endereco: int) -> tuple[LinhaCache, DetalhesCache]:
        indice, tag, deslocamento, inicio_bloco = self._partes(endereco)
        linha = self.linhas[indice]
        hit = linha.valido and linha.tag == tag
        substituiu = False
        bloco_removido = None
        if hit:
            self.estatisticas.hits += 1
        else:
            self.estatisticas.misses += 1
            if linha.valido:
                substituiu = True
                self.estatisticas.substituicoes += 1
                bloco_removido = (linha.tag * self.quantidade_linhas + indice)
            linha.dados = [self.ram.ler(i) for i in range(inicio_bloco, inicio_bloco + self.palavras_por_bloco)]
            linha.tag = tag
            linha.valido = True
            self.estatisticas.blocos_carregados += 1
        detalhes = DetalhesCache(
            endereco=endereco, indice=indice, tag=tag, deslocamento=deslocamento,
            inicio_bloco=inicio_bloco, hit=hit, substituiu=substituiu,
            bloco_removido=bloco_removido,
        )
        return linha, detalhes

    def ler(self, endereco: int) -> tuple[int, DetalhesCache]:
        linha, detalhes = self._localizar(endereco)
        self.estatisticas.leituras += 1
        return linha.dados[detalhes.deslocamento], detalhes

    def escrever(self, endereco: int, valor: int) -> DetalhesCache:
        if self.somente_leitura:
            raise PermissionError(f"Nao e permitido escrever na cache {self.nome}.")
        valor = self.ram._normalizar_palavra(valor)
        linha, detalhes = self._localizar(endereco)
        self.estatisticas.escritas += 1
        linha.dados[detalhes.deslocamento] = valor
        self.ram.escrever(endereco, valor)
        return detalhes

    def invalidar_bloco(self, endereco: int) -> bool:
        indice, tag, _deslocamento, _inicio = self._partes(endereco)
        linha = self.linhas[indice]
        if linha.valido and linha.tag == tag:
            linha.valido = False
            return True
        return False

    def limpar(self) -> None:
        self.linhas = [LinhaCache(dados=[0] * self.palavras_por_bloco)
                       for _ in range(self.quantidade_linhas)]
        self.estatisticas = EstatisticasCache()

    def visualizar(self) -> list[dict[str, object]]:
        resultado = []
        for i, linha in enumerate(self.linhas):
            bloco = (linha.tag * self.quantidade_linhas + i) if linha.valido else None
            resultado.append({
                "linha": i, "valido": linha.valido,
                "tag": linha.tag if linha.valido else None,
                "bloco_ram": bloco, "dados": list(linha.dados) if linha.valido else [],
            })
        return resultado