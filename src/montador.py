import re

opcodes_12 = {
    "LODD": 0b0000000000000000,
    "STOD": 0b0001000000000000,
    "ADDD": 0b0010000000000000,
    "SUBD": 0b0011000000000000,
    "JPOS": 0b0100000000000000,
    "JZER": 0b0101000000000000,
    "JUMP": 0b0110000000000000,
    "LOCO": 0b0111000000000000,
    "LODL": 0b1000000000000000,
    "STOL": 0b1001000000000000,
    "ADDL": 0b1010000000000000,
    "SUBL": 0b1011000000000000,
    "JNEG": 0b1100000000000000,
    "JNZE": 0b1101000000000000,
    "CALL": 0b1110000000000000,
}

opcodes_8 = {
    "INSP": 0b1111110000000000,
    "DESP": 0b1111111000000000,
}

opcodes_0 = {
    "PSHI": 0b1111000000000000,
    "POPI": 0b1111001000000000,
    "PUSH": 0b1111010000000000,
    "POP":  0b1111011000000000,
    "RETN": 0b1111100000000000,
    "SWAP": 0b1111101000000000,
}


class ErroMontagem(Exception):
    def __init__(self, mensagem, linha=None, numero_linha=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.linha = linha
        self.numero_linha = numero_linha

    def __str__(self):
        if self.numero_linha is not None:
            return f"Linha {self.numero_linha}: {self.mensagem}"
        return self.mensagem

def obter_linhas(codigo):
    if not isinstance(codigo, str):
        raise ErroMontagem("O codigo Assembly deve ser uma string.")

    linhas = []
    dentro_de_comentario = False
    inicio_comentario = None

    for numero, linha in enumerate(codigo.splitlines(), 1):
        texto = []
        indice = 0

        while indice < len(linha):
            if dentro_de_comentario:
                if linha.startswith("*/", indice):
                    dentro_de_comentario = False
                    inicio_comentario = None
                    indice += 2
                else:
                    indice += 1
                continue

            if linha.startswith("//", indice) or linha[indice] in ("#", ";"):
                break

            if linha.startswith("/*", indice):
                texto.append(" ")
                dentro_de_comentario = True
                inicio_comentario = numero
                indice += 2
                continue

            texto.append(linha[indice])
            indice += 1

        instrucao = "".join(texto).strip()
        if instrucao:
            linhas.append((numero, instrucao))

    if dentro_de_comentario:
        raise ErroMontagem("Comentario nao fechado.", numero_linha=inicio_comentario)

    return linhas

def _erro(mensagem, numero_linha, linha):
    return ErroMontagem(mensagem, linha=linha, numero_linha=numero_linha)


def _numero(texto, numero_linha, linha):
    try:
        if texto.lower().startswith(("0x", "0b", "0o")):
            return int(texto, 0)
        return int(texto, 10)
    except ValueError:
        raise _erro(f"Operando invalido: '{texto}'", numero_linha, linha)


def montar(codigo_assembly):
    memoria = [0] * 4096
    linhas = obter_linhas(codigo_assembly)
    labels = {}
    endereco = 0

    # primeira passagem para encontrar labels
    for numero, linha in linhas:
        texto = linha
        while ":" in texto:
            nome, resto = texto.split(":", 1)
            nome = nome.strip()
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nome):
                raise _erro("Nome de label invalido", numero, linha)
            if nome in labels:
                raise _erro(f"Label '{nome}' ja foi definida", numero, linha)
            labels[nome] = endereco
            texto = resto.strip()
            if not texto:
                break

        if not texto:
            continue

        nome = texto.split()[0].upper()
        if nome not in opcodes_12 and nome not in opcodes_8 and nome not in opcodes_0:
            raise _erro(f"Instrucao invalida: '{nome}'", numero, linha)
        if endereco >= len(memoria):
            raise _erro("Programa ultrapassa os limites da memoria", numero, linha)
        endereco += 1

    # segunda passagem para palavras
    endereco = 0
    for numero, linha in linhas:
        texto = linha
        while ":" in texto:
            nome, resto = texto.split(":", 1)
            nome = nome.strip()
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nome):
                texto = resto.strip()
                if not texto:
                    break
                continue
            break

        if not texto:
            continue

        partes = texto.split()
        nome = partes[0].upper()

        if nome in opcodes_12:
            if len(partes) != 2:
                raise _erro(f"'{nome}' exige um operando", numero, linha)
            operando_texto = partes[1]
            if operando_texto in labels:
                operando = labels[operando_texto]
            elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", operando_texto):
                raise _erro(f"Label nao definida: '{operando_texto}'", numero, linha)
            else:
                operando = _numero(operando_texto, numero, linha)
            if not 0 <= operando <= 0xFFF:
                raise _erro("Operando fora do intervalo de 12 bits", numero, linha)
            palavra = opcodes_12[nome] | operando
        elif nome in opcodes_8:
            if len(partes) != 2:
                raise _erro(f"'{nome}' exige um operando", numero, linha)
            operando = _numero(partes[1], numero, linha)
            if not 0 <= operando <= 0xFF:
                raise _erro("Operando fora do intervalo de 8 bits", numero, linha)
            palavra = opcodes_8[nome] | operando
        else:
            if len(partes) != 1:
                raise _erro(f"'{nome}' nao aceita operando", numero, linha)
            palavra = opcodes_0[nome]

        memoria[endereco] = palavra
        endereco += 1

    return memoria
