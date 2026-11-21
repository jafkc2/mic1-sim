from cpu.datapath import DataPath
from cpu.control_unit import UnidadeControle
import montador
from memory import ControladorMemoria
from memory.config import TAMANHO_RAM


class CPU:
    def __init__(self, programa=None):
        self.data_path = DataPath()
        self.memoria = ControladorMemoria()
        self.unidade_controle = UnidadeControle()
        self._reiniciar_execucao()

        if programa is not None:
            self.carregar_programa(programa)

    def _reiniciar_execucao(self):
        self.ciclos_executados = 0
        self.subciclos_executados = 0
        self.microinstrucoes_executadas = 0
        self.instrucoes_executadas = 0
        self.ciclos_espera = 0
        self.subciclo_atual = 0
        self.em_espera = False
        self._sinal_memoria_aberto = False
        self.programa_carregado = False
        self.tamanho_programa = 0
        self.motivo_parada = None

    @property
    def fim_programa(self) -> bool:
        return (
            self.programa_carregado
            and self.subciclo_atual == 0
            and not self.em_espera
            and not self.unidade_controle.em_execucao
            and self.unidade_controle.mpc == 0
            and (self.data_path.pc & (TAMANHO_RAM - 1)) >= self.tamanho_programa
        )

    def _entregar_resultado_memoria(self):
        resultado = self.memoria.obter_resultado()
        if resultado is None:
            raise RuntimeError("Resultado de memoria esperado, mas indisponivel.")
        if resultado.operacao == "leitura":
            self.data_path.receber_dado_memoria(resultado.valor)

    def _concluir_microinstrucao(self):
        uc = self.unidade_controle
        uc.avancar(self.data_path.flag_n, self.data_path.flag_z)
        self.microinstrucoes_executadas += 1
        if uc.mpc == 0:
            self.instrucoes_executadas += 1
        if self.fim_programa:
            self.motivo_parada = "fim_programa"

    def _finalizar_subciclo_quatro(self):
        dp = self.data_path
        uc = self.unidade_controle
        mi = uc.mir
        if mi is None:
            raise RuntimeError("Nenhuma microinstrucao carregada.")

        dp.gravar_resultado()
        confirmacao = self._sinal_memoria_aberto
        self.memoria.processar_sinais(
            mi.rd,
            mi.wr,
            dp.obter_endereco_memoria(),
            dp.obter_dado_memoria(),
            instrucao=uc.endereco_mir == 0,
        )
        self._sinal_memoria_aberto = bool(mi.rd or mi.wr) and not confirmacao
        self.memoria.avancar_ciclo()

        if confirmacao:
            if self.memoria.memoria_ocupada():
                self.em_espera = True
                return
            self._entregar_resultado_memoria()

        self._concluir_microinstrucao()

    def executar_subciclo(self) -> bool:
        if not self.programa_carregado:
            raise RuntimeError("Carregue um programa antes de executar a CPU.")
        if self.fim_programa:
            self.motivo_parada = "fim_programa"
            return False

        self.motivo_parada = None
        etapa = self.subciclo_atual + 1
        if self.em_espera:
            if etapa == 4:
                self.memoria.avancar_ciclo(espera_cpu=True)
                self.ciclos_espera += 1
                self.ciclos_executados += 1
                self.subciclo_atual = 0
                if not self.memoria.memoria_ocupada():
                    self._entregar_resultado_memoria()
                    self.em_espera = False
                    self._concluir_microinstrucao()
            else:
                self.subciclo_atual = etapa
        else:
            if etapa == 1:
                self.unidade_controle.buscar_microinstrucao()
            elif etapa == 2:
                self.data_path.carregar_latches(self.unidade_controle.mir)
            elif etapa == 3:
                self.data_path.processar_microinstrucao()
            else:
                self.subciclo_atual = 0
                self._finalizar_subciclo_quatro()
                self.ciclos_executados += 1
            if etapa != 4:
                self.subciclo_atual = etapa

        self.subciclos_executados += 1
        return True

    def executar_ciclo(self) -> bool:
        if not self.programa_carregado:
            raise RuntimeError("Carregue um programa antes de executar a CPU.")
        if self.fim_programa:
            self.motivo_parada = "fim_programa"
            return False

        self.executar_subciclo()
        while self.subciclo_atual != 0:
            self.executar_subciclo()
        return True

    @staticmethod
    def _validar_limite(valor: int, nome: str):
        if type(valor) is not int or valor <= 0:
            raise ValueError(f"{nome} deve ser um inteiro positivo.")

    def executar_microinstrucao(self, max_ciclos: int = 10000) -> bool:
        self._validar_limite(max_ciclos, "max_ciclos")
        inicio = self.microinstrucoes_executadas
        for _ in range(max_ciclos):
            if not self.executar_ciclo():
                return False
            if self.microinstrucoes_executadas > inicio:
                return True
        self.motivo_parada = "limite_ciclos"
        return False

    def executar_macroinstrucao(self, max_ciclos: int = 10000) -> bool:
        self._validar_limite(max_ciclos, "max_ciclos")
        inicio = self.instrucoes_executadas
        for _ in range(max_ciclos):
            if not self.executar_ciclo():
                return False
            if self.instrucoes_executadas > inicio:
                return True
        self.motivo_parada = "limite_ciclos"
        return False

    def executar_programa(self, max_instrucoes: int = 1000,
                          max_ciclos: int = 100000) -> str:
        self._validar_limite(max_instrucoes, "max_instrucoes")
        self._validar_limite(max_ciclos, "max_ciclos")
        if not self.programa_carregado:
            raise RuntimeError("Carregue um programa antes de executar a CPU.")

        inicio_instrucoes = self.instrucoes_executadas
        inicio_ciclos = self.ciclos_executados
        while not self.fim_programa:
            if self.instrucoes_executadas - inicio_instrucoes >= max_instrucoes:
                self.motivo_parada = "limite_instrucoes"
                return self.motivo_parada
            if self.ciclos_executados - inicio_ciclos >= max_ciclos:
                self.motivo_parada = "limite_ciclos"
                return self.motivo_parada
            self.executar_ciclo()

        self.motivo_parada = "fim_programa"
        return self.motivo_parada

    def get_estado(self) -> dict:
        return {
            "ciclos": self.ciclos_executados,
            "subciclos": self.subciclos_executados,
            "microinstrucoes": self.microinstrucoes_executadas,
            "instrucoes": self.instrucoes_executadas,
            "ciclos_espera": self.ciclos_espera,
            "subciclo_atual": self.subciclo_atual,
            "em_espera": self.em_espera,
            "mpc": self.unidade_controle.mpc,
            "endereco_mir": self.unidade_controle.endereco_mir,
            "programa_carregado": self.programa_carregado,
            "tamanho_programa": self.tamanho_programa,
            "fim_programa": self.fim_programa,
            "motivo_parada": self.motivo_parada,
        }

    def carregar_programa(self, programa: str | None):
        if programa is None:
            return

        palavras = montador.montar(programa)
        tamanho = sum(bool(linha.rsplit(":", 1)[-1].strip())
                      for _, linha in montador.obter_linhas(programa))
        self.memoria.carregar_programa(palavras)
        self.data_path.reset()
        self.unidade_controle.reset()
        self._reiniciar_execucao()
        self.programa_carregado = True
        self.tamanho_programa = tamanho

    def reset(self):
        self.memoria.reset()
        self.data_path.reset()
        self.unidade_controle.reset()
        self._reiniciar_execucao()
