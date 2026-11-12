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


def obter_linhas(codigo: str):
    # necessário: limapr o código de comentários, linhas em branco, etc. 
    return codigo.splitlines()

def montar(codigo_assembly):
    # sem suporte a labels por enquanto. Deve funcionar apenas para programas bem simples.
    # Código bem ruim, refaço dps

    memoria = [0] * 4096
    linhas = obter_linhas(codigo_assembly)
    endereco = 0

    for num, linha in enumerate(linhas):
        a = linha.split()

        nome = a[0]
        if nome in opcodes_12:
            if len(a) < 2:
                print(f"Erro na linha {num}: operando faltando")
            operando = int(a[1])

            if not (0 <= operando <= 0xfff):
                print(f"Erro na linha {num}: O operando possui tamanho incompatível")

            palavra = opcodes_12[nome] + operando   
        elif nome in opcodes_8:
            if len(a) < 2:
                print(f"Erro na linha {num}: operando faltando")
            operando = int(a[1])

            if not (0 <= operando <= 0xff):
                print(f"Erro na linha {num}: O operando possui tamanho incompatível")

            palavra = opcodes_8[nome] + operando
        elif nome in opcodes_0:
            if len(a) > 1:
                print(f"Erro na linha {num}: a operação não aceita operando")
            palavra = opcodes_0[nome]
        else:
            print(f"Linha inválida: {num}")

        memoria[endereco] = palavra
        endereco += 1


    return memoria
