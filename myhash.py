# -*- coding: utf-8 -*-
"""
Documentação do módulo myhash.py
Funções para calcular hashes CRC32, CRC64, MD5, SHA1, SHA256 e SHA512.
Autor: Uendel Rocha <uendelrocha@gmail.com>
IA: Documentado e melhorado com auxílio do Claude Sonnet AI.
Data: 2024-06-20
Este módulo fornece funções para calcular hashes de strings e arquivos
usando vários algoritmos de hash. Inclui suporte para diferentes formatos
de saída para CRC32 e CRC64.
Licença: MIT
"""
# %% Imports

# from binascii import crc32 # Apenas um wrapper para zlib.crc32
# from zlib import crc32
from my import mycrc
from hashlib import sha1 as sha160, sha256, sha512, md5
from enum import Enum

#%% CONSTANTS
class OutputFormat(Enum):
    """Formatos de saída para hash CRC32 e CRC64.
    
    Todos os lambdas recebem um inteiro (resultado do CRC) e retornam
    o valor formatado conforme especificado.
    """
    # Formatos CRC32 (32 bits / 8 dígitos hex)
    hex32  = lambda s: f'0x{s:08x}'         # CRC32: '0xXXXXXXXX'
    str32  = lambda s: f'{s:08x}'           # CRC32: 'XXXXXXXX'
    
    # Formatos CRC64 (64 bits / 16 dígitos hex)
    hex64  = lambda s: f'0x{s:016x}'        # CRC64: '0xXXXXXXXXXXXXXXXX'
    str64  = lambda s: f'{s:016x}'          # CRC64: 'XXXXXXXXXXXXXXXX'
    
    # Formatos inteiros (compatíveis com ambos)
    int64  = lambda s: s & 0xffffffffffffffff  # uint64
    int32  = lambda s: s & 0xffffffff          # uint32
    int16  = lambda s: s & 0xffff              # uint16
    bas16  = lambda s: s                       # Sem modificação

def hash_crc32(s: str, out_format: OutputFormat = OutputFormat.hex32):
    """
    Calcula CRC32 de uma string e retorna no formato especificado.
    
    Args:
        s: String de entrada
        out_format: Formato de saída (padrão: hex32)
    
    Returns:
        CRC32 formatado conforme out_format
    
    Example:
        >>> hash_crc32("123456", OutputFormat.int32)
        2286445522
        >>> hash_crc32("123456", OutputFormat.hex32)
        '0x884863d2'
        >>> hash_crc32("123456", OutputFormat.str32)
        '884863d2'
    """
    crc_int = mycrc.crc32(s.encode()) & 0xffffffff  # Garante uint32
    return out_format(crc_int)

def hash_crc64(s: str, out_format: OutputFormat = OutputFormat.hex64):
    """
    Calcula CRC64 de uma string e retorna no formato especificado.

    Args:
        s: String de entrada
        out_format: Formato de saída (padrão: hex64)
    
    Returns:
        CRC64 formatado conforme out_format

    Example:
        >>> hash_crc64("123456", OutputFormat.int64)
        7234002948248355863
        >>> hash_crc64("123456", OutputFormat.hex64)
        '0x64623a5aba0b3ea7'
        >>> hash_crc64("123456", OutputFormat.str64)
        '64623a5aba0b3ea7'
    """
    crc_int = mycrc.crc64(s.encode()) & 0xffffffffffffffff  # Garante uint64
    return out_format(crc_int)

# Funções auxiliares CRC32
def hash_crc32_hex(s: str) -> str:
    """Retorna CRC32 como '0xXXXXXXXX'"""
    return hash_crc32(s, OutputFormat.hex32)

def hash_crc32_int32(s: str) -> int:
    """Retorna CRC32 como inteiro uint32"""
    return hash_crc32(s, OutputFormat.int32)

def hash_crc32_int16(s: str) -> int:
    """Retorna CRC32 truncado para uint16"""
    return hash_crc32(s, OutputFormat.int16)

def hash_crc32_str(s: str) -> str:
    """Retorna CRC32 como string hexadecimal (8 chars)"""
    return hash_crc32(s, OutputFormat.str32)

# Funções auxiliares CRC64
def hash_crc64_hex(s: str) -> str:
    """Retorna CRC64 como '0xXXXXXXXXXXXXXXXX'"""
    return hash_crc64(s, OutputFormat.hex64)

def hash_crc64_int64(s: str) -> int:
    """Retorna CRC64 como inteiro uint64"""
    return hash_crc64(s, OutputFormat.int64)

def hash_crc64_str(s: str) -> str:
    """Retorna CRC64 como string hexadecimal (16 chars)"""
    return hash_crc64(s, OutputFormat.str64)

#%% Calcula hashes de um arquivo (colisões conhecidas 1/2^32)
# Este hash NÃO deve ser usado para guardar senhas
def crc_file(file_path):
  # Utiliza a implementação otimizada (incremental) do módulo mycrc
  return hex(mycrc.crc32_file(file_path))

#%% Calcula hashes de uma string (colisões: 1/2^32)
# Este hash NÃO deve ser usado para guardar senhas
def crc_str(s:str, encoding = 'utf-8') -> str:
  return hex(mycrc.crc32(s.encode(encoding)) & 0xffffffff)

def crc64_str(s:str, encoding = 'utf-8') -> str:
    return hex(mycrc.crc64(s.encode(encoding)) & 0xffffffffffffffff)

#%% Calcula hash md5 (colisões conhecidas 1/2^128)
# Este hash NÃO deve ser usado para guardar senhas
# MySQL: MD5(conteudo)
# Oracle: STANDARD_HASH(conteudo, 'MD5')
def md5_str(s:str, encoding = 'utf-8') -> str:
  return md5(s.encode(encoding)).hexdigest()

# Retorna os primeiros 16 dígitos hex do hash md5 como uint64
# (Usado em alguns bancos de dados NoSQL como chave primária)
# Valor máximo: 0xFFFFFFFFFFFFFFFF = 18446744073709551615 (18 quintilhões) ou 2^64-1
# MySQL: CAST(CONV(SUBSTR(MD5(conteudo), 1, 16), 16, 10) AS UNSIGNED)
# Oracle: TO_NUMBER(SUBSTR(STANDARD_HASH(conteudo, 'MD5'), 1, 16), 'XXXXXXXXXXXXXXXX')
def hash_md5_int64(s:str, encoding = 'utf-8') -> int:
  return int(md5_str(s, encoding)[:16], 16)

# Retorna os primeiros 8 dígitos hex do hash md5 como uint32
# Não recomendado para uso em produção devido ao alto risco de colisões
# Valor máximo: 0xFFFFFFFF = 4294967295
# Com apenas 77.000 registros, há 50% de chance de colisão. 
# Com 1 milhão de registros, a colisão é estatisticamente garantida.
# Usado apenas para fins educacionais ou em sistemas com poucos registros.
# O Int32 só deve ser usado se a unicidade não for crítica (ex: partition ID, bucket ID) 
# ou se o volume de dados for muito pequeno (menos de 10.000 itens).
# MySQL: CAST(CONV(SUBSTR(MD5(conteudo), 1, 8), 16, 10) AS UNSIGNED)
# Oracle: TO_NUMBER(SUBSTR(STANDARD_HASH(conteudo, 'MD5'), 1, 8), 'XXXXXXXX')
def hash_md5_int32(s:str, encoding = 'utf-8') -> int:
  return int(md5_str(s, encoding)[:8], 16)

#%% Calcula hash sha160 (colisões 1/2^160)
# Este hash NÃO deve ser usado para guardar senhas
def sha160_str(s:str, encoding = 'utf-8') -> str:
  return sha160(s.encode(encoding)).hexdigest()

def sha1(s:str, encoding = 'utf-8') -> str:
  return sha160_str(s, encoding)

#%% Calcula hash sha256 (colisões 1/2^256)
# Este hash pode ser usado para guardar senhas
def sha256_str(s:str, encoding = 'utf-8'):
  return sha256(s.encode(encoding)).hexdigest()

# Alias sha2 para sha256
def sha2(s:str, encoding = 'utf-8'):
  return sha256_str(s, encoding)

#%% Calcula hash sha512 (colisões 1/2^512)
# Este hash pode ser usado para guardar senhas
def sha512_str(s:str, encoding = 'utf-8'):
  return sha512(s.encode(encoding)).hexdigest()

# Alias sha3 para sha512
def sha3(s:str, encoding = 'utf-8'):
  return sha512_str(s, encoding)