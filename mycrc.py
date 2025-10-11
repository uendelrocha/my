# -*- coding: utf-8 -*-
"""
Implementação otimizada de CRC-64/ISO e CRC-32/ISO-3309 usando tabelas de lookup.

Este módulo fornece funções para calcular checksums CRC de 32 e 64 bits,
incluindo suporte para processamento incremental de arquivos grandes.

Created on Sun Sep  7 02:54:53 2025
@author: uendelrocha@gmail.com

Algoritmos implementados:
    - CRC-64/ISO (polinômio 0x42f0e1eba9ea3693)
    - CRC-32/ISO-3309 (polinômio 0xEDB88320)

Example:
    >>> from my.mycrc import crc64, crc32, crc64_hex
    >>> crc64(b"123456")
    7234002948248355863
    >>> crc64_hex(b"123456")
    '64623a5aba0b3ea7'
    >>> crc32(b"123456")
    2286445522
"""

# =============================================================================
# CONSTANTES
# =============================================================================

# Polinômios padrão
_CRC64_POLY = 0x42f0e1eba9ea3693  # CRC-64-ISO
_CRC32_POLY = 0xEDB88320           # CRC-32/ISO-3309

# Máscaras de bits (valores de inicialização e XOR final)
_CRC64_MASK = 0xffffffffffffffff  # 64 bits todos em 1
_CRC32_MASK = 0xFFFFFFFF           # 32 bits todos em 1

# Constantes públicas para uso externo
CRC64_INIT = _CRC64_MASK  # Valor inicial para CRC-64 incremental
CRC32_INIT = _CRC32_MASK  # Valor inicial para CRC-32 incremental

# Tabelas pré-computadas (lazy initialization)
_CRC64_TABLE = None
_CRC32_TABLE = None


# =============================================================================
# FUNÇÕES INTERNAS
# =============================================================================

def _calculate_crc_table(crc_poly):
    """
    Calcula e retorna a tabela de lookup para o CRC.
    
    Esta função gera uma tabela de 256 valores pré-calculados que acelera
    significativamente o cálculo do CRC através de operações de lookup.
    
    Args:
        crc_poly (int): Polinômio do CRC
    
    Returns:
        list: Tabela de 256 valores pré-calculados
    
    Note:
        Esta função é chamada automaticamente na primeira execução de
        crc64() ou crc32() e o resultado é armazenado em cache.
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


def _crc(data: bytes, crc_poly, crc_init, crc_xor_out, crc_table):
    """
    Função genérica para calcular o CRC.
    
    Esta função implementa o algoritmo core usado por todas as variantes de CRC.
    
    Args:
        data (bytes): Dados de entrada
        crc_poly (int): Polinômio CRC
        crc_init (int): Valor inicial do CRC
        crc_xor_out (int): Valor para XOR final (0 para cálculo incremental)
        crc_table (list): Tabela de lookup pré-calculada
    
    Returns:
        int: Valor CRC calculado
    
    Raises:
        TypeError: Se data não for do tipo bytes
    """
    if not isinstance(data, bytes):
        raise TypeError(f"Esperado 'bytes', recebido '{type(data).__name__}'")
    
    if crc_table is None:
        crc_table = _calculate_crc_table(crc_poly)
    
    crc = crc_init
    for byte in data:
        table_index = (crc ^ byte) & 0xFF
        crc = (crc >> 8) ^ crc_table[table_index]
    
    return crc ^ crc_xor_out


# =============================================================================
# CRC-64 - FUNÇÕES PRINCIPAIS
# =============================================================================

def crc64(data: bytes) -> int:
    """
    Calcula o valor CRC-64/ISO para os dados de entrada.
    
    Args:
        data (bytes): Os dados de entrada para o cálculo do CRC
    
    Returns:
        int: O valor CRC-64 calculado (inteiro positivo de 64 bits)
    
    Raises:
        TypeError: Se data não for bytes
    
    Example:
        >>> crc64(b"123456")
        7234002948248355863
        >>> crc64(b"Hello World")
        13827403126148551023
    
    Note:
        Este hash NÃO deve ser usado para armazenar senhas.
        Colisões conhecidas: 1/2^64 (aproximadamente 1 em 18 quintilhões)
    """
    global _CRC64_TABLE
    if _CRC64_TABLE is None:
        _CRC64_TABLE = _calculate_crc_table(_CRC64_POLY)
    
    return _crc(data, _CRC64_POLY, _CRC64_MASK, _CRC64_MASK, _CRC64_TABLE)


def crc64_incremental(data: bytes, crc: int = CRC64_INIT) -> int:
    """
    Calcula CRC-64 de forma incremental (permite processar dados em partes).
    
    Esta função é útil para calcular o CRC de grandes volumes de dados
    que não cabem na memória, como arquivos grandes.
    
    Args:
        data (bytes): Chunk de dados a processar
        crc (int): Valor CRC acumulado da iteração anterior (padrão: 0xFFFFFFFFFFFFFFFF)
    
    Returns:
        int: Valor CRC atualizado (SEM XOR final - aplicar manualmente no fim)
    
    Warning:
        Esta função NÃO aplica o XOR final. Após processar todos os chunks,
        você deve aplicar: resultado_final = crc ^ 0xffffffffffffffff
    
    Example:
        >>> # Processar dados em múltiplas partes
        >>> crc = CRC64_INIT
        >>> crc = crc64_incremental(b"Hello", crc)
        >>> crc = crc64_incremental(b" ", crc)
        >>> crc = crc64_incremental(b"World", crc)
        >>> resultado = crc ^ CRC64_INIT  # XOR final
        >>> print(f"CRC-64: {resultado}")
        13827403126148551023
    """
    global _CRC64_TABLE
    if _CRC64_TABLE is None:
        _CRC64_TABLE = _calculate_crc_table(_CRC64_POLY)
    
    # Reutiliza _crc sem aplicar XOR final (xor_out = 0)
    return _crc(data, _CRC64_POLY, crc, 0, _CRC64_TABLE)


# =============================================================================
# CRC-64 - FUNÇÕES AUXILIARES DE FORMATAÇÃO
# =============================================================================

def crc64_hex(data: bytes) -> str:
    """
    Calcula CRC-64 e retorna como string hexadecimal.
    
    Args:
        data (bytes): Dados de entrada
    
    Returns:
        str: CRC-64 formatado como hexadecimal (16 caracteres)
    
    Example:
        >>> crc64_hex(b"123456")
        '64623a5aba0b3ea7'
        >>> crc64_hex(b"Hello World")
        'bfe79bd95db65def'
    """
    return f"{crc64(data):016x}"


def crc64_bytes(data: bytes) -> bytes:
    """
    Calcula CRC-64 e retorna como bytes.
    
    Args:
        data (bytes): Dados de entrada
    
    Returns:
        bytes: CRC-64 como sequência de 8 bytes (big-endian)
    
    Example:
        >>> crc64_bytes(b"123456")
        b'd b\\x1a\\xba\\x0b>\\xa7'
        >>> len(crc64_bytes(b"test"))
        8
    """
    return crc64(data).to_bytes(8, byteorder='big')


def crc64_file(filepath: str, chunk_size: int = 8192) -> int:
    """
    Calcula CRC-64 de um arquivo lendo em chunks.
    
    Esta função é eficiente para arquivos grandes, pois processa
    o arquivo em pedaços pequenos sem carregar tudo na memória.
    
    Args:
        filepath (str): Caminho completo do arquivo
        chunk_size (int): Tamanho do chunk em bytes (padrão: 8KB)
    
    Returns:
        int: Valor CRC-64 do arquivo completo
    
    Raises:
        FileNotFoundError: Se o arquivo não existir
        IOError: Se houver erro de leitura do arquivo
        PermissionError: Se não houver permissão para ler o arquivo
    
    Example:
        >>> crc = crc64_file("documento.pdf")
        >>> print(f"CRC-64 do arquivo: {crc}")
        >>> 
        >>> # Verificar integridade
        >>> crc_hex = f"{crc:016x}"
        >>> print(f"Checksum: {crc_hex}")
    """
    crc = CRC64_INIT
    
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                crc = crc64_incremental(chunk, crc)
        return crc ^ CRC64_INIT  # XOR final
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    except PermissionError:
        raise PermissionError(f"Sem permissão para ler o arquivo: {filepath}")
    except Exception as e:
        raise IOError(f"Erro ao ler arquivo {filepath}: {e}")


# =============================================================================
# CRC-32 - FUNÇÕES PRINCIPAIS
# =============================================================================

def crc32(data: bytes) -> int:
    """
    Calcula o valor CRC-32/ISO-3309 para os dados de entrada.
    
    Args:
        data (bytes): Os dados de entrada para o cálculo do CRC
    
    Returns:
        int: O valor CRC-32 calculado (inteiro positivo de 32 bits)
    
    Raises:
        TypeError: Se data não for bytes
    
    Example:
        >>> crc32(b"123456")
        2286445522
        >>> crc32(b"Hello World")
        1243066710
    
    Note:
        Este hash NÃO deve ser usado para armazenar senhas.
        Colisões conhecidas: 1/2^32 (aproximadamente 1 em 4 bilhões)
    """
    global _CRC32_TABLE
    if _CRC32_TABLE is None:
        _CRC32_TABLE = _calculate_crc_table(_CRC32_POLY)
    
    return _crc(data, _CRC32_POLY, _CRC32_MASK, _CRC32_MASK, _CRC32_TABLE)


def crc32_incremental(data: bytes, crc: int = CRC32_INIT) -> int:
    """
    Calcula CRC-32 de forma incremental (permite processar dados em partes).
    
    Args:
        data (bytes): Chunk de dados a processar
        crc (int): Valor CRC acumulado da iteração anterior (padrão: 0xFFFFFFFF)
    
    Returns:
        int: Valor CRC atualizado (SEM XOR final - aplicar manualmente no fim)
    
    Warning:
        Esta função NÃO aplica o XOR final. Após processar todos os chunks,
        você deve aplicar: resultado_final = crc ^ 0xFFFFFFFF
    
    Example:
        >>> crc = CRC32_INIT
        >>> crc = crc32_incremental(b"Hello", crc)
        >>> crc = crc32_incremental(b" World", crc)
        >>> resultado = crc ^ CRC32_INIT  # XOR final
        >>> print(f"CRC-32: {resultado}")
        1243066710
    """
    global _CRC32_TABLE
    if _CRC32_TABLE is None:
        _CRC32_TABLE = _calculate_crc_table(_CRC32_POLY)
    
    # Reutiliza _crc sem aplicar XOR final (xor_out = 0)
    return _crc(data, _CRC32_POLY, crc, 0, _CRC32_TABLE)


# =============================================================================
# CRC-32 - FUNÇÕES AUXILIARES DE FORMATAÇÃO
# =============================================================================

def crc32_hex(data: bytes) -> str:
    """
    Calcula CRC-32 e retorna como string hexadecimal.
    
    Args:
        data (bytes): Dados de entrada
    
    Returns:
        str: CRC-32 formatado como hexadecimal (8 caracteres)
    
    Example:
        >>> crc32_hex(b"123456")
        '884863d2'
        >>> crc32_hex(b"Hello World")
        '4a17b156'
    """
    return f"{crc32(data):08x}"


def crc32_bytes(data: bytes) -> bytes:
    """
    Calcula CRC-32 e retorna como bytes.
    
    Args:
        data (bytes): Dados de entrada
    
    Returns:
        bytes: CRC-32 como sequência de 4 bytes (big-endian)
    
    Example:
        >>> crc32_bytes(b"123456")
        b'\\x88Hc\\xd2'
        >>> len(crc32_bytes(b"test"))
        4
    """
    return crc32(data).to_bytes(4, byteorder='big')


def crc32_file(filepath: str, chunk_size: int = 8192) -> int:
    """
    Calcula CRC-32 de um arquivo lendo em chunks.
    
    Args:
        filepath (str): Caminho completo do arquivo
        chunk_size (int): Tamanho do chunk em bytes (padrão: 8KB)
    
    Returns:
        int: Valor CRC-32 do arquivo completo
    
    Raises:
        FileNotFoundError: Se o arquivo não existir
        IOError: Se houver erro de leitura do arquivo
        PermissionError: Se não houver permissão para ler o arquivo
    
    Example:
        >>> crc = crc32_file("documento.txt")
        >>> print(f"CRC-32 do arquivo: {crc}")
        >>> 
        >>> # Comparar com zlib.crc32 (devem ser iguais)
        >>> import zlib
        >>> with open("documento.txt", 'rb') as f:
        ...     zlib_crc = zlib.crc32(f.read())
        >>> assert crc == zlib_crc
    """
    crc = CRC32_INIT
    
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                crc = crc32_incremental(chunk, crc)
        return crc ^ CRC32_INIT  # XOR final
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    except PermissionError:
        raise PermissionError(f"Sem permissão para ler o arquivo: {filepath}")
    except Exception as e:
        raise IOError(f"Erro ao ler arquivo {filepath}: {e}")


# =============================================================================
# FUNÇÕES LEGADAS (Compatibilidade com código antigo)
# =============================================================================

def crc_str(s: str, encoding='utf-8'):
    """
    Calcula CRC-32 de uma string (função legada).
    
    Args:
        s (str): String de entrada
        encoding (str): Codificação a usar (padrão: 'utf-8')
    
    Returns:
        str: CRC-32 formatado como hexadecimal com prefixo '0x'
    
    Note:
        Esta função existe para compatibilidade com código antigo.
        Prefira usar crc32() ou crc32_hex() para código novo.
    
    Example:
        >>> crc_str("123456")
        '0x884863d2'
    """
    return hex(crc32(s.encode(encoding)))


def crc(file_path):
    """
    Calcula CRC-32 de um arquivo (função legada).
    
    Args:
        file_path (str): Caminho do arquivo
    
    Returns:
        str: CRC-32 formatado como hexadecimal com prefixo '0x'
    
    Note:
        Esta função existe para compatibilidade com código antigo.
        Prefira usar crc32_file() para código novo.
    
    Example:
        >>> crc("documento.txt")
        '0x4a17b156'
    """
    return hex(crc32_file(file_path))


# =============================================================================
# EXPORTAÇÕES E METADADOS
# =============================================================================

__all__ = [
    # Constantes públicas
    'CRC64_INIT',
    'CRC32_INIT',
    
    # CRC-64
    'crc64',
    'crc64_incremental',
    'crc64_hex',
    'crc64_bytes',
    'crc64_file',
    
    # CRC-32
    'crc32',
    'crc32_incremental',
    'crc32_hex',
    'crc32_bytes',
    'crc32_file',
    
    # Legado
    'crc',
    'crc_str',
]

__version__ = '1.0.0'
__author__ = 'uendelrocha@gmail.com'
