"""Configuracoes didaticas do MAC-I/MIC-1 e de sua hierarquia de memoria."""

# A tabela MAC-I apresenta palavras de 16 bits e enderecos de 12 bits.
BITS_PALAVRA = 16
TAMANHO_RAM = 4096  # enderecos 0..4095 (4.096 palavras de 16 bits = 8 KiB)
MASCARA_PALAVRA = (1 << BITS_PALAVRA) - 1

# Valores iniciais das duas caches de mapeamento direto.
LINHAS_CACHE = 4
PALAVRAS_POR_BLOCO = 4

# Latencias DIDATICAS (nao representam ciclos fisicos do MIC-1).
# A camada da CPU integrara estes valores ao seu mecanismo de espera.
CICLOS_CONSULTA_CACHE = 1
CICLOS_ACESSO_RAM = 10
