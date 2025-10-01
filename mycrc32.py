# Polinômio CRC32 usado. Este é o polinômio CRC-32/ISO-3309.
_CRC32_POLY = 0xEDB88320

# Tabela pré-computada para o cálculo do CRC32.
_CRC32_TABLE = None

def _calculate_crc32_table():
    """
    Calcula e retorna a tabela de lookup para o CRC32.
    Esta função é chamada apenas uma vez para inicializar a tabela.
    """
    table = [0] * 256
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ _CRC32_POLY
            else:
                crc >>= 1
        table[i] = crc
    return table

def crc32(data: bytes):
    """
    Calcula o valor CRC32 para os dados de entrada.
    A entrada deve ser uma sequência de bytes.

    Args:
        data (bytes): Os dados de entrada para o cálculo do CRC.

    Returns:
        int: O valor CRC32 calculado (um inteiro de 32 bits).
    """
    global _CRC32_TABLE
    if _CRC32_TABLE is None:
        _CRC32_TABLE = _calculate_crc32_table()

    crc = 0xFFFFFFFF
    for byte in data:
        table_index = (crc ^ byte) & 0xFF
        crc = (crc >> 8) ^ _CRC32_TABLE[table_index]
        
    return crc ^ 0xFFFFFFFF