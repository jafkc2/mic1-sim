# Memoria e cache do MIC-1 — entrega inicial

Estes modulos implementam a **RAM de 4.096 palavras de 16 bits** e **duas caches independentes**, mantendo a unica RAM do MAC-I. A interface grafica ainda **nao** utiliza as caches; a futura unidade de controle deve integrar o controlador ao tratamento de `RD` e `WR`.

## Arquivos novos

- `src/config.py`: parametros padrao.
- `src/memory/ram.py`: `MemoriaRAM` — ler, escrever, carregar, limpar e visualizar.
- `src/memory/cache.py`: `CacheMapeamentoDireto` — quatro linhas, quatro palavras/bloco, tags, bits validos, hits/misses, substituicoes.
- `src/memory/memory_controller.py`: `ControladorMemoria` — I-Cache, D-Cache e latencias.
- `examples/demo_memoria.py`: exemplo executavel sem GUI.
- `tests/test_memoria.py`: testes automatizados sem bibliotecas externas.

## Usando no projeto

```python
from memory import ControladorMemoria

mem = ControladorMemoria()
mem.carregar_programa([0x7005, 0x1064])  # LOCO 5; STOD 100

instrucao = mem.ler_instrucao(0)
print(instrucao.valor, instrucao.hit, instrucao.ciclos)

mem.escrever_dado(100, 5)
dado = mem.ler_dado(100)
print(dado.valor, dado.hit)
```

O `ResultadoAcesso` carrega valor, endereco, `hit`, `indice`, `tag`, `deslocamento`, `inicio_bloco`, `ciclos`, `houve_substituicao`, `bloco_removido` e `icache_invalidada` para futura exibicao no ttk.

## Enderecamento

Enderecos de palavra de 12 bits `0..4095`. Com quatro palavras por bloco e quatro linhas, o endereco contem **8 bits de TAG, 2 bits de indice e 2 bits de deslocamento**:

- `numero_bloco = endereco // 4`
- `indice = numero_bloco % 4`
- `tag = numero_bloco // 4`
- `deslocamento = endereco % 4`

Exemplo: o endereco `21` pertence ao bloco de enderecos `20..23`, linha `1`, tag `1`, deslocamento `1`.

## Politica de escrita

A **D-Cache e write-through e write-allocate**:

- *Hit de leitura*: devolve o dado diretamente da cache.
- *Miss de leitura*: carrega o bloco da RAM e entrega a palavra solicitada.
- *Hit de escrita*: altera cache e RAM simultaneamente.
- *Miss de escrita*: primeiro carrega o bloco; depois altera cache e RAM.
- Escrita que modifica uma palavra de instrucao invalida a eventual copia de seu bloco na I-Cache.
- A I-Cache nao aceita escrita diretamente.

**Atencao:** os acessos do processador devem passar pelo `ControladorMemoria`. Escritas diretas em `ram.escrever()` servem somente para inicializacao/testes; depois de modifica-las, limpe ambas as caches, pois essa operacao ignora os mecanismos de coerencia.

## Tempos simulados

Adotamos `1 ciclo` para consultar a cache e `10 ciclos` para o custo de um acesso/transporte de bloco da RAM. Sao valores **didaticos**:

| Operacao | Hit | Miss |
|---|---:|---:|
| Leitura (I ou D) | 1 | 11 |
| Escrita D (write-through + write-allocate) | 11 | 21 |

**Importante:** o controlador calcula o custo, mas ainda **nao interrompe a CPU**, pois `UnidadeControle` e seus subciclos estao em desenvolvimento. Na integracao futura, uma solicitacao `RD`/`WR` tera estado pendente e sera concluida apenas uma vez; o motor devera introduzir os ciclos de espera adicionais sem duplicar as leituras/escritas presentes no microprograma. Esses custos nao devem ser adicionados cegamente aos microciclos ja existentes.

## Executar testes

```bash
python -m unittest discover -s tests -v
python examples/demo_memoria.py
```

O projeto original usa `customtkinter`; nenhuma dessas duas rotinas depende de interface grafica ou de dependencias externas.

## O que falta integrar (responsabilidade da CPU/GUI)

1. `MAR` seleciona endereco; `RD/WR` inicia operacao unica pelo controlador.
2. `MBR` recebe a palavra lida so quando a requisicao terminar.
3. `RD` repetido no microprograma nao pode iniciar nova leitura se ja houver uma pendente.
4. Ciclos de espera de miss nao devem modificar registradores indevidamente.
5. A GUI consumira `visualizar()` e `ultimo_acesso` para pintar linhas, tags, hits e misses.
6. Futuras variantes: associativa, conjunto, FIFO/LRU, write-back, dirty bit.

## Arquivos do restante do grupo

O restante do codigo foi preservado. Apenas `src/cpu/cpu.py` recebeu uma adaptacao **minima** para o construtor `CPU()` nao tentar montar `None`, instanciar o controlador e carregar programas na RAM. A CPU ainda nao executa instrucoes; os metodos correspondentes lancam `NotImplementedError` para deixar essa pendencia explicita. A interface atual ainda usa `customtkinter` e nao foi alterada.
