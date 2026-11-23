from __future__ import annotations

import customtkinter as ctk

from cpu.cpu import CPU
from cpu.datapath import DataPath
from cpu.microprogram import Condicao, Microinstrucao
from .cores import Paleta


class PainelMicroprograma(Paleta, ctk.CTkFrame):

    def __init__(self, master, cpu: CPU):
        super().__init__(master, fg_color=self.FUNDO)
        self.cpu = cpu
        self._enderecos = []
        self._botoes = {}
        self._microinstrucoes = {}
        self._selecao_manual = False
        self._selecionada = 0
        self._cores_anteriores = {}

        uc = cpu.unidade_controle
        for endereco, palavra in enumerate(uc.rom):
            if palavra is not None:
                self._enderecos.append(endereco)
                self._microinstrucoes[endereco] = Microinstrucao.decodificar(palavra)

        self.grid_columnconfigure(0, weight=0, minsize=300)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        titulo = ctk.CTkFrame(self, fg_color="transparent")
        titulo.grid(row=0, column=0, columnspan=2, padx=14, pady=(12, 5), sticky="ew")
        titulo.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            titulo, text="Unidade de Controle · ROM Microprogramada",
            font=ctk.CTkFont(size=19, weight="bold"), text_color=self.TEXTO,
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            titulo,
            text=f"{len(self._enderecos)}/256 posições programadas · 32 bits por palavra",
            text_color=self.SECUNDARIO,
        ).grid(row=0, column=1, padx=8, sticky="e")

        status = ctk.CTkFrame(self, fg_color=self.PAINEL, corner_radius=7)
        status.grid(row=1, column=0, columnspan=2, sticky="ew", padx=14, pady=8)
        for coluna in range(4):
            status.grid_columnconfigure(coluna, weight=1)
        self._valores_status = {}
        for col, (nome, rotulo) in enumerate([
            ("MPC", "Próximo endereço"), ("MIR", "Microinstrução atual"),
            ("FLAGS", "Flags N/Z"), ("CLOCK", "Ciclos / Subciclos"),
        ]):
            item = ctk.CTkFrame(status, fg_color="transparent")
            item.grid(row=0, column=col, sticky="ew", padx=10, pady=7)
            ctk.CTkLabel(item, text=rotulo, text_color=self.SECUNDARIO,
                         font=ctk.CTkFont(size=11)).pack(anchor="w")
            valor = ctk.CTkLabel(item, text="—", text_color=self.TEXTO,
                                 font=ctk.CTkFont(size=17, weight="bold"))
            valor.pack(anchor="w")
            self._valores_status[nome] = valor

        esquerda = ctk.CTkFrame(self, fg_color=self.PAINEL, corner_radius=8)
        esquerda.grid(row=2, column=0, sticky="nsew", padx=(14, 7), pady=(3, 12))
        esquerda.grid_columnconfigure(0, weight=1)
        esquerda.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(esquerda, text="Endereços da ROM", text_color=self.TEXTO,
                     font=ctk.CTkFont(size=15, weight="bold")).grid(
                         row=0, column=0, sticky="w", padx=12, pady=(12, 2))
        ctk.CTkLabel(esquerda, text="Verde: próximo MPC   ·   Âmbar: MIR",
                     text_color=self.SECUNDARIO, font=ctk.CTkFont(size=11)).grid(
                         row=1, column=0, sticky="w", padx=12, pady=(0, 6))
        self.lista_rom = ctk.CTkScrollableFrame(
            esquerda, fg_color="transparent", width=272,
        )
        self.lista_rom.grid(row=2, column=0, sticky="nsew", padx=7, pady=(0, 8))
        self.lista_rom.grid_columnconfigure(0, weight=1)
        for i, endereco in enumerate(self._enderecos):
            palavra = self.cpu.unidade_controle.rom[endereco]
            botao = ctk.CTkButton(
                self.lista_rom, text=f"{endereco:03d}    0x{palavra:08X}",
                font=ctk.CTkFont(family="Consolas", size=12),
                text_color=self.SECUNDARIO, anchor="w", height=29, corner_radius=5,
                fg_color="#192a40", hover_color="#2b4462", border_width=1,
                border_color="#273b55", command=lambda e=endereco: self.selecionar(e),
            )
            botao.grid(row=i, column=0, sticky="ew", pady=2)
            self._botoes[endereco] = botao

        direita = ctk.CTkFrame(self, fg_color=self.PAINEL, corner_radius=8)
        direita.grid(row=2, column=1, sticky="nsew", padx=(7, 14), pady=(3, 12))
        direita.grid_columnconfigure(0, weight=1)
        direita.grid_rowconfigure(3, weight=1)
        topo = ctk.CTkFrame(direita, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        topo.grid_columnconfigure(0, weight=1)
        self.titulo_inspecao = ctk.CTkLabel(
            topo, text="Inspeção da microinstrução", font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.TEXTO,
        )
        self.titulo_inspecao.grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            topo, text="Seguir execução", width=125, height=28,
            fg_color="#1f4761", hover_color="#2c6687", command=self.seguir_execucao,
        ).grid(row=0, column=1, padx=(8, 0))

        self.rotulo_binario = ctk.CTkLabel(
            direita, text="", text_color=self.AZUL,
            font=ctk.CTkFont(family="Consolas", size=13), anchor="w",
        )
        self.rotulo_binario.grid(row=1, column=0, sticky="ew", padx=14, pady=5)
        self.rotulo_operacao = ctk.CTkLabel(
            direita, text="", text_color=self.SECUNDARIO,
            justify="left", anchor="w", wraplength=560,
            font=ctk.CTkFont(size=12),
        )
        self.rotulo_operacao.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 6))

        detalhes = ctk.CTkScrollableFrame(direita, fg_color="transparent")
        detalhes.grid(row=3, column=0, sticky="nsew", padx=11, pady=(0, 10))
        detalhes.grid_columnconfigure(0, weight=1)
        detalhes.grid_columnconfigure(1, weight=1)
        self._campos = {}
        nomes = ["AMUX", "COND", "ALU", "SH", "MBR", "MAR", "RD", "WR",
                 "ENC", "C", "B", "A", "ADDR"]
        for i, nome in enumerate(nomes):
            linha = i // 2
            coluna = i % 2
            item = ctk.CTkFrame(detalhes, fg_color="#1a2b42", corner_radius=6)
            item.grid(row=linha, column=coluna, sticky="ew", padx=4, pady=4)
            item.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(item, text=nome, text_color=self.SECUNDARIO,
                         font=ctk.CTkFont(size=11, weight="bold")).grid(
                             row=0, column=0, padx=9, pady=(6, 0), sticky="w")
            rotulo = ctk.CTkLabel(item, text="—", text_color=self.TEXTO,
                                  font=ctk.CTkFont(size=12))
            rotulo.grid(row=1, column=0, padx=9, pady=(0, 7), sticky="w")
            self._campos[nome] = (item, rotulo)

        self._cache_inspecao = None
        self.atualizar()

    @staticmethod
    def _nome_registrador(numero):
        if 0 <= numero < len(DataPath.NOMES_REGISTRADORES):
            return DataPath.NOMES_REGISTRADORES[numero]
        return str(numero)

    def _descrever(self, mi: Microinstrucao):
        operacoes_ula = ("A + B", "A AND B", "A", "NOT A")
        deslocamentos = ("Sem deslocamento", "Esquerda 1 bit", "Direita 1 bit")
        condicoes = ("Sequencial", "Se N = 1", "Se Z = 1", "Incondicional")
        origem_a = "MBR" if mi.amux else self._nome_registrador(mi.a)
        origem_b = self._nome_registrador(mi.b)
        destino = self._nome_registrador(mi.c) if mi.enc else "Nenhum"
        extras = []
        if mi.mar:
            extras.append("MAR ← Latch B")
        if mi.mbr:
            extras.append("MBR ← Shifter")
        if mi.rd:
            extras.append("RD")
        if mi.wr:
            extras.append("WR")
        final = "; ".join(extras) if extras else "Sem acesso à memória"
        if mi.cond == Condicao.SEQUENCIAL:
            proximo = "Sequencial"
        else:
            proximo = f"{condicoes[mi.cond]} → {mi.addr}"
        return (
            f"ULA: {operacoes_ula[mi.alu]}  ·  SH: {deslocamentos[mi.sh]}\n"
            f"Entrada A: {origem_a}  ·  Entrada B: {origem_b}  ·  C: {destino}\n"
            f"{final}\nPróximo endereço: {proximo}"
        )

    def _inspecionar(self, endereco):
        if endereco not in self._microinstrucoes:
            self.titulo_inspecao.configure(text=f"Endereço {endereco:03d} não programado")
            return
        if self._cache_inspecao == endereco:
            return
        self._cache_inspecao = endereco
        mi = self._microinstrucoes[endereco]
        palavra = mi.codificar()
        self.titulo_inspecao.configure(text=f"Microinstrução {endereco:03d}")
        self.rotulo_binario.configure(
            text=f"0x{palavra:08X}   {palavra:032b}"
        )
        self.rotulo_operacao.configure(text=self._descrever(mi))
        sinais = mi.sinais()
        for nome, (item, rotulo) in self._campos.items():
            valor = sinais[nome]
            if nome in ("A", "B", "C"):
                descricao = f"{valor}  ({self._nome_registrador(valor)})"
            elif nome == "COND":
                descricao = ("Sequencial", "N", "Z", "Sempre")[valor]
            elif nome == "ADDR":
                descricao = str(valor)
            else:
                descricao = str(valor)
            rotulo.configure(text=descricao, text_color=self.LARANJA if nome in ("RD", "WR", "MAR", "MBR", "ENC") and valor else self.TEXTO)
            item.configure(border_width=1 if nome in ("RD", "WR", "MAR", "MBR", "ENC") and valor else 0,
                           border_color=self.LARANJA)

    def selecionar(self, endereco: int):
        self._selecao_manual = True
        self._selecionada = endereco
        self._inspecionar(endereco)
        self._atualizar_cores()

    def seguir_execucao(self):
        self._selecao_manual = False
        self.atualizar()

    def _atualizar_cores(self):
        uc = self.cpu.unidade_controle
        for endereco, botao in self._botoes.items():
            selecionado = endereco == self._selecionada
            em_mir = uc.endereco_mir == endereco
            proximo = uc.mpc == endereco
            estilo = (
                "#25405b" if selecionado else "#192a40",
                self.LARANJA if em_mir else (self.VERDE if proximo else "#273b55"),
                self.TEXTO if (selecionado or em_mir or proximo) else self.SECUNDARIO,
                2 if (em_mir or proximo or selecionado) else 1,
            )
            if self._cores_anteriores.get(endereco) == estilo:
                continue
            botao.configure(fg_color=estilo[0], border_color=estilo[1],
                            text_color=estilo[2], border_width=estilo[3])
            self._cores_anteriores[endereco] = estilo

    def atualizar(self):
        cpu = self.cpu
        uc = cpu.unidade_controle
        dp = cpu.data_path
        self._valores_status["MPC"].configure(text=f"{uc.mpc:03d}")
        mir = "—" if uc.endereco_mir is None else f"{uc.endereco_mir:03d}"
        self._valores_status["MIR"].configure(text=mir)
        self._valores_status["FLAGS"].configure(text=f"N={int(dp.flag_n)}  Z={int(dp.flag_z)}")
        self._valores_status["CLOCK"].configure(
            text=f"{cpu.ciclos_executados} / {cpu.subciclos_executados}"
        )
        if not self._selecao_manual:
            alvo = uc.endereco_mir if uc.em_execucao and uc.endereco_mir is not None else uc.mpc
            if alvo not in self._microinstrucoes and uc.endereco_mir in self._microinstrucoes:
                alvo = uc.endereco_mir
            if alvo in self._microinstrucoes:
                self._selecionada = alvo
        self._inspecionar(self._selecionada)
        self._atualizar_cores()
