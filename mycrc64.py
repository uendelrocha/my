# -*- coding: utf-8 -*-
"""
Created on Sun Sep  7 02:54:53 2025

@author:uendelrocha@gmail.com
            
"""


# Polinômio CRC64 usado. Este é um polinômio comum para CRC64.
_CRC64_POLY = 0x42f0e1eba9ea3693

# Tabela pré-computada para o cálculo do CRC64.
_CRC64_TABLE = None

def _calculate_crc64_table():
    """
    Calcula e retorna a tabela de lookup para o CRC64.
    Esta função é chamada apenas uma vez para inicializar a tabela.
    """
    table = [0] * 256
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ _CRC64_POLY
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
        _CRC64_TABLE = _calculate_crc64_table()

    crc = 0xffffffffffffffff
    for byte in data:
        table_index = (crc ^ byte) & 0xff
        crc = (crc >> 8) ^ _CRC64_TABLE[table_index]
        
    return crc ^ 0xffffffffffffffff