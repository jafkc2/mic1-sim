from __future__ import annotations

import customtkinter as ctk

from cpu.cpu import CPU
from ..cores import Paleta


class PainelCache(Paleta, ctk.CTkFrame):

    def __init__(self, master, cpu: CPU):
        super().__init__(master, fg_color=self.FUNDO)
        self.cpu = cpu
        self._linhas_cache = {}
        self._indicadores = {}
        self._resumos = {}
        self._inspecao_cache = ctk.StringVar(value="I-Cache")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 5))
        cabecalho.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            cabecalho, text="Memória Cache", text_color=self.TEXTO,
            font=ctk.CTkFont(size=21, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        cache = cpu.memoria.icache
        ctk.CTkLabel(
            cabecalho,
            text=(f"I-Cache e D-Cache  ·  {cache.quantidade_linhas} linhas × "
                  f"{cache.palavras_por_bloco} palavras  ·  mapeamento direto  ·  write-through / write-allocate"),
            text_color=self.SECUNDARIO, font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, sticky="w", pady=(1, 0))

        self.corpo = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
            scrollbar_button_color="#334d69",
            scrollbar_button_hover_color="#476a91",
        )
        self.corpo.grid(row=1, column=0, sticky="nsew", padx=(9, 3), pady=(3, 9))
        self.corpo.grid_columnconfigure(0, weight=1, uniform="cache")
        self.corpo.grid_columnconfigure(1, weight=1, uniform="cache")

        indicadores = ctk.CTkFrame(self.corpo, fg_color="transparent")
        indicadores.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 10))
        for coluna in range(5):
            indicadores.grid_columnconfigure(coluna, weight=1, uniform="indicadores")
        for coluna, (chave, titulo) in enumerate((
            ("acessos", "ACESSOS"), ("hits", "HITS"),
            ("misses", "MISSES"), ("taxa", "TAXA DE HIT"),
            ("amat", "AMAT (LEITURAS)"),
        )):
            quadro = ctk.CTkFrame(indicadores, fg_color=self.PAINEL, corner_radius=8,
                                  border_color=self.BORDA, border_width=1)
            quadro.grid(row=0, column=coluna, sticky="ew", padx=3)
            ctk.CTkLabel(quadro, text=titulo, text_color=self.SECUNDARIO,
                         font=ctk.CTkFont(size=10, weight="bold")).pack(pady=(9, 1))
            valor = ctk.CTkLabel(quadro, text="0", text_color=self.TEXTO,
                                 font=ctk.CTkFont(size=23, weight="bold"))
            valor.pack(pady=(0, 9))
            self._indicadores[chave] = valor

        self._criar_cache("I", 0)
        self._criar_cache("D", 1)
        self._criar_operacao()
        self._criar_inspecao()
        self.atualizar()

    def _texto(self, master, texto, cor=None, tamanho=12, negrito=False, **kwargs):
        return ctk.CTkLabel(
            master, text=texto, text_color=cor or self.TEXTO,
            font=ctk.CTkFont(size=tamanho, weight="bold" if negrito else "normal"),
            **kwargs,
        )

    def _criar_cache(self, tipo, coluna):
        cor = self.AZUL if tipo == "I" else self.VERDE
        titulo = "I-Cache · Instruções" if tipo == "I" else "D-Cache · Dados"
        quadro = ctk.CTkFrame(self.corpo, fg_color=self.PAINEL, corner_radius=9,
                              border_width=1, border_color=self.BORDA)
        quadro.grid(row=1, column=coluna, sticky="nsew", padx=4, pady=(0, 10))
        quadro.grid_columnconfigure(0, weight=1)

        topo = ctk.CTkFrame(quadro, fg_color="transparent")
        topo.grid(row=0, column=0, padx=13, pady=(11, 6), sticky="ew")
        topo.grid_columnconfigure(0, weight=1)
        self._texto(topo, titulo, cor, 17, True).grid(row=0, column=0, sticky="w")
        resumo = self._texto(topo, "0 leituras  ·  0 escritas  ·  0 hits  ·  0 misses",
                             self.SECUNDARIO, 11)
        resumo.grid(row=1, column=0, sticky="w", pady=(2, 0))
        self._resumos[tipo] = resumo

        cab = ctk.CTkFrame(quadro, fg_color=self.CABECALHO, corner_radius=3)
        cab.grid(row=1, column=0, padx=12, pady=(4, 3), sticky="ew")
        cab.grid_columnconfigure(4, weight=1)
        for col, texto in enumerate(("LINHA", "V", "TAG", "BLOCO RAM", "PALAVRAS (16 BITS)")):
            self._texto(cab, texto, self.SECUNDARIO, 10, True).grid(
                row=0, column=col, padx=(5, 3), pady=7,
                sticky="w" if col == 4 else "n")

        linhas = ctk.CTkFrame(quadro, fg_color="transparent")
        linhas.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 10))
        linhas.grid_columnconfigure(0, weight=1)
        self._linhas_cache[tipo] = []
        cache = self.cpu.memoria.icache if tipo == "I" else self.cpu.memoria.dcache
        for indice in range(cache.quantidade_linhas):
            linha = ctk.CTkFrame(linhas, fg_color=self.PAINEL_INTERNO, corner_radius=5,
                                 border_width=1, border_color=self.BORDA)
            linha.grid(row=indice, column=0, sticky="ew", pady=2)
            linha.grid_columnconfigure(4, weight=1)
            elementos = []
            for coluna_label, largura in enumerate((34, 20, 43, 67, 215)):
                label = self._texto(linha, "—", self.TEXTO, 11,
                                    coluna_label == 0, width=largura)
                label.grid(row=0, column=coluna_label, padx=(5, 3), pady=12,
                           sticky="w" if coluna_label == 4 else "n")
                elementos.append(label)
            self._linhas_cache[tipo].append((linha, elementos))

        rodape = self._texto(quadro, "Substituições: 0   ·   Blocos carregados: 0",
                            self.SECUNDARIO, 11)
        rodape.grid(row=3, column=0, padx=13, pady=(0, 12), sticky="w")
        self._resumos[tipo + "_rodape"] = rodape

    def _criar_operacao(self):
        quadro = ctk.CTkFrame(self.corpo, fg_color=self.PAINEL, corner_radius=9,
                              border_width=1, border_color=self.BORDA)
        quadro.grid(row=2, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 10))
        quadro.grid_columnconfigure(0, weight=1)
        self._texto(quadro, "Operações e temporização", self.TEXTO, 15, True).grid(
            row=0, column=0, sticky="w", padx=13, pady=(11, 2))
        self.label_operacao = self._texto(quadro, "Nenhum acesso realizado.",
                                         self.SECUNDARIO, 12, anchor="w", justify="left")
        self.label_operacao.grid(row=1, column=0, sticky="ew", padx=13, pady=(2, 3))
        self.progresso = ctk.CTkProgressBar(
            quadro, height=9, fg_color=self.CABECALHO, progress_color=self.AZUL,
        )
        self.progresso.grid(row=2, column=0, padx=13, pady=(4, 10), sticky="ew")
        self.progresso.set(0)
        self.label_espera = self._texto(quadro, "Ciclos de espera da CPU: 0",
                                       self.SECUNDARIO, 11)
        self.label_espera.grid(row=3, column=0, sticky="w", padx=13, pady=(0, 12))

    def _criar_inspecao(self):
        quadro = ctk.CTkFrame(self.corpo, fg_color=self.PAINEL, corner_radius=9,
                              border_width=1, border_color=self.BORDA)
        quadro.grid(row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 12))
        quadro.grid_columnconfigure(4, weight=1)
        self._texto(quadro, "Inspecionar endereço sem acessar a memória", self.TEXTO,
                    15, True).grid(row=0, column=0, columnspan=5, padx=13,
                                   pady=(10, 2), sticky="w")
        self._texto(quadro, "Endereço", self.SECUNDARIO, 11).grid(
            row=1, column=0, padx=(13, 5), pady=7)
        self.entrada_endereco = ctk.CTkEntry(quadro, width=112, placeholder_text="0x0064")
        self.entrada_endereco.grid(row=1, column=1, padx=3, pady=7)
        self.entrada_endereco.bind("<Return>", lambda _e: self.inspecionar_endereco())
        self.seletor_cache = ctk.CTkOptionMenu(
            quadro, values=["I-Cache", "D-Cache"], variable=self._inspecao_cache,
            width=113, fg_color=self.BOTAO_AZUL, button_color=self.BOTAO_AZUL_HOVER,
            button_hover_color=self.BOTAO_AZUL_ALTERNATIVO_HOVER,
        )
        self.seletor_cache.grid(row=1, column=2, padx=4, pady=7)
        ctk.CTkButton(
            quadro, text="Inspecionar", command=self.inspecionar_endereco,
            width=105, fg_color=self.BOTAO_AZUL, hover_color=self.BOTAO_AZUL_HOVER,
        ).grid(row=1, column=3, padx=4, pady=7)
        self.label_inspecao = self._texto(
            quadro, "Informe um endereço em decimal ou hexadecimal (0x...).",
            self.SECUNDARIO, 11, anchor="w", justify="left",
        )
        self.label_inspecao.grid(row=2, column=0, columnspan=5, padx=13,
                                 pady=(2, 12), sticky="ew")

    def inspecionar_endereco(self):
        texto = self.entrada_endereco.get().strip()
        try:
            endereco = int(texto, 16 if texto.lower().startswith("0x") else 10)
            cache = (self.cpu.memoria.icache if self._inspecao_cache.get() == "I-Cache"
                     else self.cpu.memoria.dcache)
            partes = cache.decompor_endereco(endereco)
        except (ValueError, TypeError) as erro:
            self.label_inspecao.configure(text=f"Endereço inválido: {erro}",
                                          text_color=self.VERMELHO)
            return
        linha = cache.linhas[partes["indice"]]
        presente = linha.valido and linha.tag == partes["tag"]
        status = "PRESENTE NA CACHE" if presente else "AUSENTE DA CACHE"
        cor = self.VERDE if presente else self.AMARELO
        self.label_inspecao.configure(
            text=(f"0x{endereco:03X} ({endereco})  ·  TAG: 0x{partes['tag']:02X}  ·  "
                  f"LINHA: {partes['indice']}  ·  DESLOCAMENTO: {partes['deslocamento']}  ·  {status}"),
            text_color=cor,
        )

    def atualizar(self):
        memoria = self.cpu.memoria
        ci, cd = memoria.icache, memoria.dcache
        estatisticas = memoria.get_estatisticas()
        acessos = ci.estatisticas.acessos + cd.estatisticas.acessos
        self._indicadores["acessos"].configure(text=str(acessos))
        self._indicadores["hits"].configure(text=str(estatisticas["hits"]),
                                            text_color=self.VERDE)
        self._indicadores["misses"].configure(text=str(estatisticas["misses"]),
                                              text_color=self.AMARELO)
        taxa = (estatisticas["hits"] / acessos * 100) if acessos else 0.0
        self._indicadores["taxa"].configure(text=f"{taxa:.1f}%")
        self._indicadores["amat"].configure(text=f"{estatisticas['amat']:.2f} ciclos")
        self.label_espera.configure(
            text=(f"Ciclos de espera da CPU: {estatisticas['ciclos_espera_cpu']}   ·   "
                  f"Leituras RAM: {estatisticas['acessos_ram_leitura']}   ·   "
                  f"Escritas RAM: {estatisticas['acessos_ram_escrita']}   ·   "
                  f"Média escrita: {estatisticas['latencia_media_escrita']:.2f} ciclos")
        )

        pendente = memoria.requisicao_pendente
        ultimo = memoria.ultimo_acesso
        ativo = pendente if pendente is not None else ultimo
        for tipo, cache in (("I", ci), ("D", cd)):
            e = cache.estatisticas
            self._resumos[tipo].configure(
                text=(f"{e.leituras} leituras  ·  {e.escritas} escritas  ·  "
                      f"{e.hits} hits  ·  {e.misses} misses  ·  hit: {e.taxa_hit*100:.1f}%")
            )
            self._resumos[tipo + "_rodape"].configure(
                text=f"Substituições: {e.substituicoes}   ·   Blocos carregados: {e.blocos_carregados}")
            for dados, (quadro, labels) in zip(cache.visualizar(), self._linhas_cache[tipo]):
                indice = dados["linha"]
                destaque = ativo is not None and ativo.cache == tipo and ativo.endereco // cache.palavras_por_bloco % cache.quantidade_linhas == indice
                em_andamento = destaque and pendente is not None
                cor = self.AMARELO if em_andamento else (self.VERDE if destaque and ativo.hit else self.VERMELHO if destaque else self.BORDA)
                quadro.configure(border_color=cor,
                                 fg_color=self.DESTAQUE_CACHE if destaque else self.PAINEL_INTERNO)
                valido = dados["valido"]
                labels[0].configure(text=f"{indice:02d}")
                labels[1].configure(text="1" if valido else "0",
                                    text_color=self.VERDE if valido else self.SECUNDARIO)
                labels[2].configure(text=f"{dados['tag']:02X}" if valido else "—")
                labels[3].configure(text=str(dados["bloco_ram"]) if valido else "—")
                palavras = "  ".join(f"{palavra:04X}" for palavra in dados["dados"])
                labels[4].configure(text=palavras if valido else "—  —  —  —")

        if pendente is not None:
            self.label_operacao.configure(
                text=(f"EM ANDAMENTO  ·  {pendente.cache}-Cache  ·  {pendente.operacao}  ·  "
                      f"endereço 0x{pendente.endereco:03X}  ·  "
                      f"{'HIT' if pendente.hit else 'MISS'}  ·  "
                      f"{pendente.ciclos_restantes}/{pendente.ciclos_totais} ciclos restantes"),
                text_color=self.AMARELO,
            )
            self.progresso.configure(progress_color=self.AMARELO)
            self.progresso.set(
                (pendente.ciclos_totais - pendente.ciclos_restantes)
                / pendente.ciclos_totais
            )
        elif ultimo is not None:
            invalidacao = "  ·  I-Cache invalidada" if ultimo.icache_invalidada else ""
            substituicao = "  ·  substituição de bloco" if ultimo.houve_substituicao else ""
            self.label_operacao.configure(
                text=(f"ÚLTIMO ACESSO  ·  {ultimo.cache}-Cache  ·  {ultimo.operacao}  ·  "
                      f"endereço 0x{ultimo.endereco:03X}  ·  "
                      f"{'HIT' if ultimo.hit else 'MISS'}  ·  {ultimo.ciclos} ciclos"
                      f"{substituicao}{invalidacao}"),
                text_color=self.VERDE if ultimo.hit else self.AMARELO,
            )
            self.progresso.configure(progress_color=self.VERDE if ultimo.hit else self.AMARELO)
            self.progresso.set(1)
        else:
            self.label_operacao.configure(text="Nenhum acesso realizado.",
                                          text_color=self.SECUNDARIO)
            self.progresso.set(0)
        if self.entrada_endereco.get().strip():
            self.inspecionar_endereco()
