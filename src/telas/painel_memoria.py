from __future__ import annotations

import customtkinter as ctk

from cpu.cpu import CPU
from .cores import Paleta


class PainelMemoria(Paleta, ctk.CTkFrame):

    def __init__(self, master, cpu: CPU | None = None, compacto: bool = False):
        super().__init__(master, fg_color=self.FUNDO if not compacto else "transparent")
        self.cpu = cpu if cpu is not None else master.cpu
        self.compacto = compacto
        self.inicio = 0
        self.quantidade = 16 if compacto else 32
        self.endereco_selecionado = None
        self._ultimo_conteudo = None
        self._alterados = set()
        self._ultimo_endereco_escrito = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2 if not compacto else 1, weight=1)

        if compacto:
            ctk.CTkLabel(
                self, text="Memória RAM · primeiras 16 palavras",
                font=ctk.CTkFont(size=15, weight="bold"),
            ).grid(row=0, column=0, sticky="w", padx=7, pady=(6, 2))
        else:
            cabecalho = ctk.CTkFrame(self, fg_color="transparent")
            cabecalho.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
            cabecalho.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                cabecalho, text="Memória principal · RAM",
                font=ctk.CTkFont(size=21, weight="bold"), text_color=self.TEXTO,
            ).grid(row=0, column=0, sticky="w")
            self.label_resumo = ctk.CTkLabel(
                cabecalho, text="", text_color=self.SECUNDARIO, anchor="w",
            )
            self.label_resumo.grid(row=1, column=0, sticky="ew", pady=(2, 0))
            self._criar_navegacao()

        self.texto_memoria = ctk.CTkTextbox(
            self, height=132 if compacto else 415,
            font=ctk.CTkFont(family="Courier New", size=11 if compacto else 13),
            fg_color=self.PAINEL, text_color=self.TEXTO,
            corner_radius=7, wrap="none",
        )
        self.texto_memoria.grid(
            row=1 if compacto else 2, column=0, sticky="nsew",
            padx=8 if compacto else 14, pady=(3, 8) if compacto else (5, 9),
        )
        self.texto_memoria.tag_config("mar", background=self.BOTAO_AZUL, foreground="#ffffff")
        self.texto_memoria.tag_config("escrito", background="#735524", foreground="#ffffff")
        self.texto_memoria.tag_config("selecionado", background="#233f52", foreground="#ffffff")
        self.texto_memoria.configure(state="disabled")

        if not compacto:
            self.label_legenda = ctk.CTkLabel(
                self,
                text="Azul: MAR  ·  Amarelo: última alteração  ·  Azul-escuro: endereço selecionado  ·  Consulta sem alterar as caches",
                text_color=self.SECUNDARIO, anchor="w",
                font=ctk.CTkFont(size=11),
            )
            self.label_legenda.grid(row=3, column=0, sticky="ew", padx=17, pady=(0, 11))
        self.atualizar()

    def _criar_navegacao(self):
        barra = ctk.CTkFrame(self, fg_color=self.PAINEL, corner_radius=8,
                             border_color=self.BORDA, border_width=1)
        barra.grid(row=1, column=0, padx=14, pady=5, sticky="ew")
        barra.grid_columnconfigure(9, weight=1)
        ctk.CTkLabel(barra, text="Endereço", text_color=self.SECUNDARIO).grid(
            row=0, column=0, padx=(12, 4), pady=11)
        self.entrada_endereco = ctk.CTkEntry(
            barra, width=98, placeholder_text="0x00FF",
        )
        self.entrada_endereco.grid(row=0, column=1, padx=3, pady=9)
        self.entrada_endereco.bind("<Return>", lambda _e: self.ir_endereco())
        ctk.CTkButton(barra, text="Ir", width=40, command=self.ir_endereco).grid(
            row=0, column=2, padx=3)
        ctk.CTkButton(barra, text="MAR", width=50, command=self.ir_mar).grid(
            row=0, column=3, padx=3)
        ctk.CTkButton(barra, text="Início", width=59, command=self.primeira).grid(
            row=0, column=4, padx=3)
        ctk.CTkButton(barra, text="◀", width=36, command=self.anterior).grid(
            row=0, column=5, padx=3)
        ctk.CTkButton(barra, text="▶", width=36, command=self.proxima).grid(
            row=0, column=6, padx=3)
        ctk.CTkButton(barra, text="Fim", width=51, command=self.ultima).grid(
            row=0, column=7, padx=3)
        self.seletor_quantidade = ctk.CTkOptionMenu(
            barra, width=82, values=["16", "32", "64", "128"],
            command=self.mudar_quantidade,
        )
        self.seletor_quantidade.set(str(self.quantidade))
        self.seletor_quantidade.grid(row=0, column=8, padx=(6, 8))
        self.label_intervalo = ctk.CTkLabel(
            barra, text="", text_color=self.SECUNDARIO, anchor="e",
            font=ctk.CTkFont(size=11),
        )
        self.label_intervalo.grid(row=0, column=9, sticky="ew", padx=(3, 12))
        self.label_erro = ctk.CTkLabel(
            barra, text="", text_color=self.VERMELHO, anchor="w",
            font=ctk.CTkFont(size=11),
        )
        self.label_erro.grid(row=1, column=0, columnspan=10, sticky="ew", padx=12)

    def _limite(self):
        return self.cpu.memoria.ram.tamanho

    def _posicionar(self, endereco):
        limite = self._limite()
        if type(endereco) is not int or not 0 <= endereco < limite:
            raise ValueError(f"Endereço fora da RAM (0 a {limite - 1}).")
        self.endereco_selecionado = endereco
        self.inicio = min(endereco // self.quantidade * self.quantidade,
                          max(0, limite - self.quantidade))
        self.label_erro.configure(text="")
        self.atualizar()

    def ir_endereco(self):
        texto = self.entrada_endereco.get().strip()
        try:
            endereco = int(texto, 16 if texto.lower().startswith("0x") else 10)
            self._posicionar(endereco)
        except ValueError as erro:
            self.label_erro.configure(text=f"Endereço inválido: {erro}")

    def ir_mar(self):
        self._posicionar(self.cpu.data_path.mar)

    def primeira(self):
        self._posicionar(0)

    def ultima(self):
        self._posicionar(self._limite() - 1)

    def anterior(self):
        self.inicio = max(0, self.inicio - self.quantidade)
        self.endereco_selecionado = None
        self.label_erro.configure(text="")
        self.atualizar()

    def proxima(self):
        self.inicio = min(max(0, self._limite() - self.quantidade),
                          self.inicio + self.quantidade)
        self.endereco_selecionado = None
        self.label_erro.configure(text="")
        self.atualizar()

    def mudar_quantidade(self, valor):
        self.quantidade = int(valor)
        self.inicio = min(self.inicio // self.quantidade * self.quantidade,
                          max(0, self._limite() - self.quantidade))
        self.atualizar()

    def atualizar(self):
        ram = self.cpu.memoria.ram
        snapshot = tuple(valor for _, valor in ram.visualizar(0, ram.tamanho))
        if self._ultimo_conteudo is not None and snapshot != self._ultimo_conteudo:
            self._alterados = {
                endereco for endereco, (antes, depois) in
                enumerate(zip(self._ultimo_conteudo, snapshot)) if antes != depois
            }
            if len(self._alterados) == 1:
                self._ultimo_endereco_escrito = next(iter(self._alterados))
            else:
                self._ultimo_endereco_escrito = None
        self._ultimo_conteudo = snapshot

        if self.compacto:
            self.inicio = 0
            self.quantidade = 16
        tamanho = min(self.quantidade, ram.tamanho - self.inicio)
        mar = self.cpu.data_path.mar
        linhas = []
        for endereco, valor in ram.visualizar(self.inicio, tamanho):
            if self.compacto:
                linhas.append(f"0x{endereco:03X}: {valor:016b}")
            else:
                linhas.append(
                    f"{endereco:4d}  0x{endereco:03X}  │  "
                    f"{valor:5d}  0x{valor:04X}  │  {valor:016b}"
                )
        self.texto_memoria.configure(state="normal")
        self.texto_memoria.delete("1.0", "end")
        self.texto_memoria.insert("1.0", "\n".join(linhas))
        for indice in range(tamanho):
            endereco = self.inicio + indice
            ini, fim = f"{indice + 1}.0", f"{indice + 1}.end"
            if endereco in self._alterados:
                self.texto_memoria.tag_add("escrito", ini, fim)
            if endereco == self.endereco_selecionado:
                self.texto_memoria.tag_add("selecionado", ini, fim)
            if endereco == mar:
                self.texto_memoria.tag_add("mar", ini, fim)
        self.texto_memoria.configure(state="disabled")
        if not self.compacto:
            self.label_intervalo.configure(
                text=f"{self.inicio}–{self.inicio + tamanho - 1} / {ram.tamanho - 1}"
            )
            ultima = (f" · Última alteração: {self._ultimo_endereco_escrito}"
                      if self._ultimo_endereco_escrito is not None else "")
            self.label_resumo.configure(
                text=f"{ram.tamanho:,} palavras de 16 bits  ·  MAR: {mar}  ·  "
                     f"PC: {self.cpu.data_path.pc}{ultima}".replace(",", ".")
            )
