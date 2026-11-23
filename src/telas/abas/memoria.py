from __future__ import annotations

import customtkinter as ctk
from cpu.cpu import CPU
from ..cores import Paleta


class PainelMemoria(Paleta, ctk.CTkFrame):
    def __init__(self, master, cpu: CPU | None = None, compacto: bool = False):
        super().__init__(master, fg_color="transparent" if compacto else self.FUNDO)
        self.cpu = cpu if cpu is not None else master.cpu
        self.compacto = compacto
        self.inicio, self.quantidade = 0, 16 if compacto else 32
        self.endereco_selecionado = None
        self._ultimo_conteudo, self._alterados, self._ultimo_endereco_escrito = None, set(), None
        self._ultima_exibicao = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1 if compacto else 2, weight=1)

        if compacto:
            ctk.CTkLabel(self, text="Memória RAM · primeiras 16 palavras",
                         text_color=self.TEXTO, font=ctk.CTkFont(size=15, weight="bold")
                         ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 4))
        else:
            cab = ctk.CTkFrame(self, fg_color="transparent")
            cab.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
            cab.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(cab, text="Memória principal · RAM", text_color=self.TEXTO,
                         font=ctk.CTkFont(size=24, weight="bold")
                         ).grid(row=0, column=0, sticky="w")
            self.label_resumo = ctk.CTkLabel(cab, text="", anchor="w", text_color=self.SECUNDARIO)
            self.label_resumo.grid(row=1, column=0, sticky="ew")
            self._criar_navegacao()

        self.texto_memoria = ctk.CTkTextbox(
            self, height=145 if compacto else 440, wrap="none", corner_radius=7,
            font=ctk.CTkFont(family="Courier New", size=13 if compacto else 16),
            fg_color=self.PAINEL, text_color=self.TEXTO,
        )
        self.texto_memoria.grid(row=1 if compacto else 2, column=0, sticky="nsew",
                                 padx=8 if compacto else 14, pady=(3, 8))
        for tag, cor in (("mar", self.BOTAO_AZUL), ("escrito", "#735524"),
                         ("selecionado", "#233f52")):
            self.texto_memoria.tag_config(tag, background=cor, foreground="#ffffff")
        self.texto_memoria.configure(state="disabled")
        if not compacto:
            ctk.CTkLabel(
                self, text="Azul: MAR  ·  Amarelo: alteração  ·  Azul-escuro: selecionado  ·  Inspeção sem acessar as caches",
                text_color=self.SECUNDARIO, anchor="w", font=ctk.CTkFont(size=12),
            ).grid(row=3, column=0, sticky="ew", padx=17, pady=(0, 9))
        self.atualizar()

    def _criar_navegacao(self):
        barra = ctk.CTkFrame(self, fg_color=self.PAINEL)
        barra.grid(row=1, column=0, sticky="ew", padx=14, pady=5)
        barra.grid_columnconfigure(9, weight=1)
        ctk.CTkLabel(barra, text="Endereço").grid(row=0, column=0, padx=(9, 3), pady=8)
        self.entrada_endereco = ctk.CTkEntry(barra, width=90, placeholder_text="0x00FF")
        self.entrada_endereco.grid(row=0, column=1, padx=2)
        self.entrada_endereco.bind("<Return>", lambda _: self.ir_endereco())
        for i, (nome, acao, largura) in enumerate((
            ("Ir", self.ir_endereco, 40), ("MAR", self.ir_mar, 45),
            ("Início", self.primeira, 56), ("◀", self.anterior, 34),
            ("▶", self.proxima, 34), ("Fim", self.ultima, 46),
        ), 2):
            ctk.CTkButton(barra, text=nome, width=largura, command=acao).grid(
                row=0, column=i, padx=2)
        self.seletor_quantidade = ctk.CTkOptionMenu(
            barra, width=76, values=["16", "32", "64", "128"], command=self.mudar_quantidade)
        self.seletor_quantidade.set(str(self.quantidade))
        self.seletor_quantidade.grid(row=0, column=8, padx=6)
        self.label_intervalo = ctk.CTkLabel(barra, text="", text_color=self.SECUNDARIO)
        self.label_intervalo.grid(row=0, column=9, sticky="e", padx=8)
        self.label_erro = ctk.CTkLabel(barra, text="", text_color=self.VERMELHO, anchor="w")
        self.label_erro.grid(row=1, column=0, columnspan=10, sticky="ew", padx=10)

    def _posicionar(self, endereco):
        tamanho = self.cpu.memoria.ram.tamanho
        if type(endereco) is not int or not 0 <= endereco < tamanho:
            raise ValueError(f"Endereço fora da RAM (0 a {tamanho - 1}).")
        self.endereco_selecionado = endereco
        self.inicio = endereco // self.quantidade * self.quantidade
        self.label_erro.configure(text="")
        self.atualizar()

    def ir_endereco(self):
        texto = self.entrada_endereco.get().strip()
        try:
            self._posicionar(int(texto, 16 if texto.lower().startswith("0x") else 10))
        except ValueError as erro:
            self.label_erro.configure(text=f"Endereço inválido: {erro}")

    def ir_mar(self):
        self._posicionar(self.cpu.data_path.mar)

    def primeira(self):
        self._posicionar(0)

    def ultima(self):
        self._posicionar(self.cpu.memoria.ram.tamanho - 1)

    def _pagina(self, passo):
        ultimo = (self.cpu.memoria.ram.tamanho - 1) // self.quantidade * self.quantidade
        self.inicio = max(0, min(ultimo, self.inicio + passo * self.quantidade))
        self.endereco_selecionado = None
        self.label_erro.configure(text="")
        self.atualizar()

    def anterior(self):
        self._pagina(-1)

    def proxima(self):
        self._pagina(1)

    def mudar_quantidade(self, valor):
        referencia = self.endereco_selecionado if self.endereco_selecionado is not None else self.inicio
        self.quantidade = int(valor)
        self.inicio = referencia // self.quantidade * self.quantidade
        self.atualizar()

    def atualizar(self):
        ram = self.cpu.memoria.ram
        snapshot = tuple(ram._palavras)
        if self._ultimo_conteudo is not None and snapshot != self._ultimo_conteudo:
            self._alterados = {i for i, (a, b) in enumerate(zip(self._ultimo_conteudo, snapshot)) if a != b}
            self._ultimo_endereco_escrito = next(iter(self._alterados)) if len(self._alterados) == 1 else None
        self._ultimo_conteudo = snapshot
        if self.compacto:
            self.inicio, self.quantidade = 0, 16
        mar = self.cpu.data_path.mar
        fim = min(ram.tamanho, self.inicio + self.quantidade)
        valores = snapshot[self.inicio:fim]
        estado = (self.inicio, valores, mar, self.endereco_selecionado,
                  frozenset(self._alterados & set(range(self.inicio, fim))))
        if estado != self._ultima_exibicao:
            pos = self.texto_memoria.yview()[0] if self._ultima_exibicao and self._ultima_exibicao[0] == self.inicio else 0
            linhas = [f"0x{e:03X}: {v:016b}" if self.compacto else
                      f"{e:4d}  0x{e:03X}  │  {v:5d}  0x{v:04X}  │  {v:016b}"
                      for e, v in enumerate(valores, self.inicio)]
            txt = self.texto_memoria
            txt.configure(state="normal")
            txt.delete("1.0", "end")
            txt.insert("1.0", "\n".join(linhas))
            for i, endereco in enumerate(range(self.inicio, fim), 1):
                ini, final = f"{i}.0", f"{i}.end"
                for tag, ativo in (("escrito", endereco in self._alterados),
                                   ("selecionado", endereco == self.endereco_selecionado),
                                   ("mar", endereco == mar)):
                    if ativo:
                        txt.tag_add(tag, ini, final)
            txt.configure(state="disabled")
            txt.yview_moveto(pos)
            self._ultima_exibicao = estado
        if not self.compacto:
            ultimo = f" · Última alteração: {self._ultimo_endereco_escrito}" if self._ultimo_endereco_escrito is not None else ""
            self.label_intervalo.configure(text=f"{self.inicio}–{fim - 1} / {ram.tamanho - 1}")
            self.label_resumo.configure(text=(
                f"{ram.tamanho:,} palavras de 16 bits · MAR: {mar} · PC: {self.cpu.data_path.pc}{ultimo}"
            ).replace(",", "."))
