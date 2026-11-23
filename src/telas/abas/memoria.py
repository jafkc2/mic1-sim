from __future__ import annotations

import customtkinter as ctk

from cpu.cpu import CPU
from ..cores import Paleta


class PainelMemoria(Paleta, ctk.CTkFrame):

    def __init__(self, master, cpu: CPU | None = None, compacto: bool = False):
        super().__init__(master, fg_color=self.FUNDO if not compacto else "transparent")
        self.cpu = cpu if cpu is not None else master.cpu
        self.compacto = compacto
        self.inicio = 0
        self.quantidade = 16 if compacto else 128
        self.endereco_selecionado = None
        self._ultimo_conteudo = None
        self._alterados = set()
        self._ultimo_endereco_escrito = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2 if not compacto else 1, weight=1)

        if compacto:
            ctk.CTkLabel(
                self, text="Memória RAM · primeiras 16 palavras",
                text_color=self.TEXTO,
                font=ctk.CTkFont(size=15, weight="bold"),
            ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 4))
        else:
            cabecalho = ctk.CTkFrame(self, fg_color="transparent")
            cabecalho.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
            cabecalho.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                cabecalho, text="Memória principal · RAM",
                font=ctk.CTkFont(size=24, weight="bold"), text_color=self.TEXTO,
            ).grid(row=0, column=0, sticky="w")
            self.label_resumo = ctk.CTkLabel(
                cabecalho, text="", text_color=self.SECUNDARIO, anchor="w",
                font=ctk.CTkFont(size=14),
            )
            self.label_resumo.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        self.texto_memoria = ctk.CTkTextbox(
            self, height=220 if compacto else 600,
            font=ctk.CTkFont(family="Courier New", size=15 if compacto else 18),
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
                font=ctk.CTkFont(size=13),
            )
            self.label_legenda.grid(row=3, column=0, sticky="ew", padx=17, pady=(0, 11))
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
        else:
            self.inicio = 0
            self.quantidade = ram.tamanho
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
            ultima = (f" · Última alteração: {self._ultimo_endereco_escrito}"
                      if self._ultimo_endereco_escrito is not None else "")
            self.label_resumo.configure(
                text=f"{ram.tamanho:,} palavras de 16 bits  ·  MAR: {mar}  ·  "
                     f"PC: {self.cpu.data_path.pc}{ultima}".replace(",", ".")
            )
