# -*- coding: utf-8 -*-
"""
Created on Sun Sep  7 02:54:53 2025
@author:uendelrocha@gmail.com
"""

# Polinômio comum usado para CRC.
_CRC64_POLY = 0x42f0e1eba9ea3693  # Este é o polinômio CRC-64-ISO.
_CRC32_POLY = 0xEDB88320  # Este é o polinômio CRC-32/ISO-3309.

# Tabela pré-computada para o cálculo do CRC.
_CRC64_TABLE = None
_CRC32_TABLE = None

def _calculate_crc_table(crc_poly):
    """
    Calcula e retorna a tabela de lookup para o CRC conforme o polinômio informado.
    Esta função é chamada apenas uma vez para inicializar a tabela.
    """
    table = [0] * 256
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ crc_poly
            else:
                crc >>= 1
        table[i] = crc
    return table

def crc64(data: bytes):
    """
    Calcula o valor CRC64 para os dados de entrada.
    A entrada deve ser uma sequência de bytes.

    Args:
        data (bytes): Os dados de entrada para o cálculo do CRC.

    Returns:
        int: O valor CRC64 calculado (um inteiro de 64 bits).
    """
    global _CRC64_TABLE
    if _CRC64_TABLE is None:
        _CRC64_TABLE = _calculate_table(_CRC64_POLY)

    crc = 0xffffffffffffffff
    for byte in data:
        table_index = (crc ^ byte) & 0xff
        crc = (crc >> 8) ^ _CRC64_TABLE[table_index]
        
    return crc ^ 0xffffffffffffffff


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
        _CRC32_TABLE = _calculate_table(_CRC32_POLY)

    crc = 0xFFFFFFFF
    for byte in data:
        table_index = (crc ^ byte) & 0xFF
        crc = (crc >> 8) ^ _CRC32_TABLE[table_index]
        
    return crc ^ 0xFFFFFFFF