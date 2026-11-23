from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from cpu.cpu import CPU
from .cores import Paleta


class PainelDatapath(Paleta, ctk.CTkFrame):
    LARGURA = 1120
    ALTURA = 710
    CORES = Paleta.ETAPAS

    def __init__(self, master, cpu: CPU):
        super().__init__(master, fg_color=self.FUNDO)
        self.cpu = cpu
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 5))
        cabecalho.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            cabecalho, text="Microarquitetura MIC-1",
            text_color=self.TEXTO, font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        self.label_etapa = ctk.CTkLabel(
            cabecalho, text="Aguardando programa", text_color=self.SECUNDARIO,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.label_etapa.grid(row=0, column=1, padx=10, sticky="e")

        self.canvas = tk.Canvas(
            self, background=self.FUNDO, borderwidth=0, highlightthickness=0,
            relief="flat",
        )
        self.canvas.grid(row=1, column=0, padx=8, pady=3, sticky="nsew")
        self.canvas.bind("<Configure>", lambda _event: self._desenhar())

        self.label_detalhes = ctk.CTkLabel(
            self, text="", anchor="w", justify="left", wraplength=1100,
            font=ctk.CTkFont(size=12), text_color=self.SECUNDARIO,
        )
        self.label_detalhes.grid(row=2, column=0, padx=16, pady=(3, 10), sticky="ew")
        self.atualizar()

    def _etapa(self) -> int:
        if not self.cpu.programa_carregado or self.cpu.subciclos_executados == 0:
            return 0
        if self.cpu.em_espera:
            return 5
        if self.cpu.subciclo_atual:
            return self.cpu.subciclo_atual
        return 4

    @staticmethod
    def _hex(valor: int, largura: int = 4) -> str:
        return f"{valor & 0xFFFF:0{largura}X}"

    def atualizar(self):
        etapa = self._etapa()
        rotulos = {
            0: "Sem execução", 1: "1 · Busca na ROM", 2: "2 · Barramentos e latches",
            3: "3 · ULA e Shifter", 4: "4 · Escrita e sequenciamento", 5: "Espera da memória",
        }
        self.label_etapa.configure(text=rotulos[etapa], text_color=self.CORES[etapa])

        cpu = self.cpu
        uc = cpu.unidade_controle
        mi = uc.mir
        if mi is None:
            detalhe = "Carregue um programa e execute um subciclo para acompanhar os caminhos de dados."
        else:
            endereco = uc.endereco_mir
            campos = [f"MI {endereco:02d}", f"AMUX={mi.amux}", f"ALU={mi.alu}",
                      f"SH={mi.sh}", f"ENC={mi.enc}", f"C={mi.c}",
                      f"RD={mi.rd}", f"WR={mi.wr}"]
            if cpu.em_espera:
                campos.append(f"memória: {cpu.memoria.ciclos_restantes} ciclo(s) restante(s)")
            detalhe = "  ·  ".join(campos)
        self.label_detalhes.configure(text=detalhe)
        self._desenhar()

    def _desenhar(self):
        canvas = self.canvas
        if not canvas.winfo_exists():
            return
        canvas.delete("all")
        largura = canvas.winfo_width()
        altura = canvas.winfo_height()
        if largura < 40 or altura < 40:
            return

        escala = min((largura - 12) / self.LARGURA, (altura - 12) / self.ALTURA)
        desloc_x = (largura - self.LARGURA * escala) / 2
        desloc_y = (altura - self.ALTURA * escala) / 2

        def p(x, y):
            return desloc_x + x * escala, desloc_y + y * escala

        def fonte(tamanho: int, negrito=False):
            return ("DejaVu Sans", max(7, int(tamanho * escala)), "bold" if negrito else "normal")

        def texto(x, y, valor, tamanho=13, cor=None, negrito=False, ancora="center"):
            canvas.create_text(*p(x, y), text=str(valor), fill=cor or self.TEXTO,
                               font=fonte(tamanho, negrito), anchor=ancora)

        def caixa(x1, y1, x2, y2, titulo, subtitulo="", ativo=False, cor=None, fundo=None):
            cor_ativa = cor or self.CORES[etapa]
            canvas.create_rectangle(*p(x1, y1), *p(x2, y2),
                                    outline=cor_ativa if ativo else self.BORDA,
                                    fill=fundo or (self.PAINEL_INTERNO if ativo else self.PAINEL),
                                    width=max(1, 2 * escala) if ativo else max(1, escala))
            centro = (x1 + x2) / 2
            if subtitulo:
                texto(centro, y1 + (y2-y1)*0.37, titulo, 15, self.TEXTO, True)
                texto(centro, y1 + (y2-y1)*0.74, subtitulo, 12,
                      cor_ativa if ativo else self.SECUNDARIO)
            else:
                texto(centro, (y1+y2)/2, titulo, 15, self.TEXTO, True)

        def linha(pontos, ativo=False, cor=None, largura_linha=3, seta=True):
            coords = []
            for x, y in pontos:
                coords.extend(p(x, y))
            canvas.create_line(
                *coords, fill=(cor or self.CORES[etapa]) if ativo else self.BORDA,
                width=max(1, (largura_linha if ativo else 1.6) * escala),
                arrow=tk.LAST if seta else tk.NONE, arrowshape=(8*escala, 10*escala, 4*escala),
                joinstyle=tk.ROUND,
            )

        cpu = self.cpu
        dp = cpu.data_path
        uc = cpu.unidade_controle
        mi = uc.mir
        etapa = self._etapa()
        regs = dp.get_registradores()
        bus = dp.get_barramentos()
        latches = dp.get_latches()
        sinais = uc.get_sinais()
        leitura = bool(mi and mi.rd)
        escrita = bool(mi and mi.wr)
        leitura_instrucao = leitura and uc.endereco_mir in (0, 1)
        acesso_dados = escrita or (leitura and not leitura_instrucao)
        usa_a = bool(mi and not mi.amux)
        usa_mbr = bool(mi and mi.amux)
        escreve_c = bool(mi and mi.enc)

        caixa(20, 15, 1100, 116, "", fundo="#101d30")
        texto(42, 34, "UNIDADE DE CONTROLE", 16, self.SECUNDARIO, True, "w")
        caixa(38, 49, 200, 100, "MPC", f"{uc.mpc:03d}", etapa == 1, self.CORES[1])
        caixa(220, 49, 390, 100, "ROM", "256 × 32 bits", etapa == 1, self.CORES[1])
        caixa(410, 49, 594, 100, "MIR", "—" if uc.endereco_mir is None else f"endereço {uc.endereco_mir:03d}", etapa == 1, self.CORES[1])
        caixa(613, 49, 773, 100, "FLAGS", f"N={int(dp.flag_n)}   Z={int(dp.flag_z)}", etapa == 3, self.CORES[3])
        caixa(793, 49, 1081, 100, "SINAIS",
              "sem microinstrução" if mi is None else f"RD:{mi.rd}  WR:{mi.wr}  ENC:{mi.enc}  COND:{mi.cond}",
              etapa in (1, 4), self.CORES[1 if etapa == 1 else 4])
        linha([(200, 75), (220, 75)], etapa == 1, self.CORES[1])
        linha([(390, 75), (410, 75)], etapa == 1, self.CORES[1])

        caixa(20, 142, 349, 529, "", fundo="#101d30")
        texto(39, 163, "BANCO DE REGISTRADORES", 15, self.SECUNDARIO, True, "w")
        nomes = dp.NOMES_REGISTRADORES
        nomes_a = dp.NOMES_REGISTRADORES[mi.a] if mi else None
        nomes_b = dp.NOMES_REGISTRADORES[mi.b] if mi else None
        nome_c = dp.NOMES_REGISTRADORES[mi.c] if mi and mi.enc else None
        for i, nome in enumerate(nomes):
            col, row = i % 3, i // 3
            x = 32 + col * 103
            y = 193 + row * 52
            valor = regs.get(nome, 0)
            eh_ativo = ((etapa == 2 and nome in (nomes_a, nomes_b)) or
                        (etapa == 4 and escreve_c and nome == nome_c))
            canvas.create_rectangle(*p(x, y), *p(x+94, y+44),
                                    fill=self.PAINEL_INTERNO if eh_ativo else self.PAINEL,
                                    outline=self.CORES[etapa] if eh_ativo else self.BORDA,
                                    width=max(1, 2*escala) if eh_ativo else max(1, escala))
            texto(x+47, y+13, nome, 12, self.TEXTO, True)
            texto(x+47, y+31, self._hex(valor), 13,
                  self.CORES[etapa] if eh_ativo else self.SECUNDARIO)

        texto(425, 149, "BARRAMENTO A", 12, self.CORES[2] if etapa == 2 else self.SECUNDARIO)
        texto(426, 294, "BARRAMENTO B", 12, self.CORES[2] if etapa == 2 else self.SECUNDARIO)
        caixa(416, 171, 547, 244, "LATCH A", f"0x{self._hex(latches['A'])}", etapa == 2, self.CORES[2])
        caixa(416, 316, 547, 389, "LATCH B", f"0x{self._hex(latches['B'])}", etapa == 2, self.CORES[2])
        linha([(349, 213), (375, 213), (416, 213)], etapa == 2, self.CORES[2])
        linha([(349, 355), (375, 355), (416, 355)], etapa == 2, self.CORES[2])
        texto(377, 228, f"{self._hex(bus['A'])}", 10, self.SECUNDARIO)
        texto(377, 371, f"{self._hex(bus['B'])}", 10, self.SECUNDARIO)

        caixa(620, 196, 732, 269, "AMUX", f"{mi.amux if mi else 0} · 0x{self._hex(dp.saida_amux)}",
              etapa == 3, self.CORES[3])
        linha([(547, 204), (620, 217)], etapa == 3 and usa_a, self.CORES[3])
        caixa(418, 448, 547, 505, "MBR", f"0x{self._hex(dp.mbr)}",
              (etapa == 3 and usa_mbr) or (etapa == 4 and bool(mi and mi.mbr)),
              self.CORES[3 if etapa == 3 else 4])
        linha([(547, 477), (589, 477), (589, 247), (620, 247)],
              etapa == 3 and usa_mbr, self.CORES[3])

        caixa(772, 271, 904, 353, "ULA", f"0x{self._hex(dp.saida_ula)}",
              etapa == 3, self.CORES[3])
        caixa(963, 282, 1090, 348, "SHIFTER", f"0x{self._hex(bus['C'])}",
              etapa == 3, self.CORES[3])
        linha([(732, 234), (752, 234), (752, 297), (772, 297)], etapa == 3, self.CORES[3])
        linha([(547, 354), (734, 354), (734, 326), (772, 326)], etapa == 3, self.CORES[3])
        linha([(904, 312), (963, 312)], etapa == 3, self.CORES[3])
        texto(821, 366, f"N={int(dp.flag_n)}  Z={int(dp.flag_z)}", 12, self.SECUNDARIO)

        caixa(418, 545, 547, 604, "MAR", f"0x{self._hex(dp.mar, 3)}",
              etapa == 3 and bool(mi and mi.mar), self.CORES[3])
        linha([(547, 355), (568, 355), (568, 575), (547, 575)],
              etapa == 3 and bool(mi and mi.mar), self.CORES[3])

        caixa(621, 448, 806, 528, "MEMÓRIA", "Controlador · RD/WR",
              etapa in (4, 5) and (leitura or escrita), self.CORES[5 if etapa == 5 else 4])
        if leitura:
            linha([(621, 482), (547, 482)], etapa in (4, 5), self.CORES[4])
        else:
            linha([(547, 482), (621, 482)], etapa in (4, 5) and escrita, self.CORES[4])
        linha([(547, 579), (578, 579), (578, 496), (621, 496)],
              etapa in (4, 5) and (leitura or escrita), self.CORES[4])
        caixa(835, 428, 951, 490, "I-CACHE", "4 × 4 palavras",
              etapa in (4, 5) and leitura_instrucao, self.CORES[5 if etapa == 5 else 4])
        caixa(968, 428, 1090, 490, "D-CACHE", "4 × 4 palavras",
              etapa in (4, 5) and acesso_dados, self.CORES[5 if etapa == 5 else 4])
        caixa(849, 542, 1081, 602, "RAM", "4096 palavras de 16 bits",
              etapa == 5, self.CORES[5])
        linha([(806, 474), (835, 462)], etapa in (4, 5) and leitura_instrucao,
              self.CORES[5 if etapa == 5 else 4])
        linha([(806, 496), (940, 496), (968, 462)], etapa in (4, 5) and acesso_dados,
              self.CORES[5 if etapa == 5 else 4])
        linha([(895, 490), (895, 542)], etapa == 5, self.CORES[5])
        linha([(1027, 490), (1027, 542)], etapa == 5, self.CORES[5])

        linha([(1026, 348), (1026, 397), (1106, 397), (1106, 634), (186, 634), (186, 529)],
              etapa == 4 and (escreve_c or bool(mi and mi.mbr)), self.CORES[4])
        texto(665, 620, "BARRAMENTO C  ·  " + f"0x{self._hex(bus['C'])}",
              13, self.CORES[4] if etapa == 4 else self.SECUNDARIO, True)
        texto(29, 673, "ETAPAS", 11, self.SECUNDARIO, True, "w")
        legenda = [("ROM", 1), ("LATCHES", 2), ("ULA", 3), ("ESCRITA", 4), ("MEMÓRIA OCUPADA", 5)]
        for i, (nome, codigo) in enumerate(legenda):
            x = 115 + 200 * i
            canvas.create_rectangle(*p(x, 660), *p(x+15, 675), fill=self.CORES[codigo], outline="")
            texto(x+24, 669, nome, 10, self.SECUNDARIO, ancora="w")
