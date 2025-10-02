# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 22:31:29 2023

@author: uendel
"""

#%% IMPORTS
import os
import shutil
from myterminal import cll, print_erro, print_aviso, print_ok, OK
from myconstant import SLASH
# from binascii import crc32 # Apenas um wrapper para zlib.crc32
import zlib
from hashlib import sha1 as sha160, sha256, sha512, md5
from enum import Enum

#%% CONSTANTS

class OutputFormat(Enum):
    hex0x = lambda s: '0x{:08x}'.format(s) # Formato hexadecimal com prefixo 0x
    int32 = lambda s: int(s, 16) & 0xffffffff # Números positivos com 32 bits
    int16 = lambda s: int(s, 16) & 0xffff # Números positivos com 16 bits
    bas16 = lambda s: int(s, 16) # Inteiro de 32 bits na base 16 (com sinal)
    str8x = lambda s: format(s, '08x') # Formato string hexadecimal de 8 caracteres

def hash_crc32(s, out_format: OutputFormat = OutputFormat.hex0x):
    return out_format(zlib.crc32(s.encode()))

def hash_crc32_hex(s):
    return hash_crc32(s, OutputFormat.hex0x)

def hash_crc32_int32(s):
    return hash_crc32(s, OutputFormat.int32)

def hash_crc32_int16(s):
    return hash_crc32(s, OutputFormat.int16)

def hash_crc32_bas16(s):
    return hash_crc32(s, OutputFormat.bas16)

def hash_crc32_str8x(s):
    return hash_crc32(s, OutputFormat.str8x)

def hash_sha256_int64(s: str, encoding='utf-8') -> int:
    """
    Retorna os primeiros 64 bits do SHA-256 como inteiro
    Muito mais seguro que CRC64
    """
    hash_bytes = sha256(s.encode(encoding)).digest()
    return int.from_bytes(hash_bytes[:8], byteorder='big')

#%% Calcula hashes de um arquivo (colisões conhecidas 1/2^32)
# Este hash NÃO deve ser usado para guardar senhas
def crc(file_path):
  with open(file_path, 'rb') as f:
    return hex(crc32(f.read()) & 0xffffffff)

#%% Calcula hashes de uma string (colisões: 1/2^32)
# Este hash NÃO deve ser usado para guardar senhas
def crc_str(s:str, encoding = 'utf-8'):
  return hex(crc32(s.encode(encoding)) & 0xffffffff)

#%% Calcula hash md5 (colisões conhecidas 1/2^128)
# Este hash NÃO deve ser usado para guardar senhas
def md5_str(s:str, encoding = 'utf-8'):
  return md5(s.encode(encoding)).hexdigest()

#%% Calcula hash sha160 (colisões 1/2^160)
# Este hash NÃO deve ser usado para guardar senhas
def sha160_str(s:str, encoding = 'utf-8'):
  return sha160(s.encode(encoding)).hexdigest()

def sha1(s:str, encoding = 'utf-8'):
  return sha160_str(s, encoding)


#%% Calcula hash sha256 (colisões 1/2^256)
# Este hash pode ser usado para guardar senhas
def sha256_str(s:str, encoding = 'utf-8'):
  return sha256(s.encode(encoding)).hexdigest()

def sha2(s:str, encoding = 'utf-8'):
  return sha256_str(s, encoding)

#%% Calcula hash sha512 (colisões 1/2^512)
# Este hash pode ser usado para guardar senhas
def sha512_str(s:str, encoding = 'utf-8'):
  return sha512(s.encode(encoding)).hexdigest()

def sha3(s:str, encoding = 'utf-8'):
  return sha512_str(s, encoding)

#%% Retorna uma lista de arquivos salvos no formato parquet no diretorio informado
def dir_files(prefix = 'pecas', extension = None, path=f".{SLASH}"):

  files_size = 0
  # Todos os arquivos do diretório
  files = [file for file in os.listdir(path=path) if os.path.isfile(path + file)]

  # Todos os arquivos com extensão informado em sufix_name
  if type(extension) is str:
    extension = [extension]
  if extension != []:
    files = [file for file in files if str(file).split('.')[-1] in extension]

  # Todos os arquivos com parte inicial informada em prefix_name
  if prefix:
    temp = [[0]*len(files),[0]*len(files)]
    for file, i in zip(files, range(len(files))):
      if len(str(file)) >= len(prefix):
        if str(file)[0:len(prefix)] == str(prefix):
          temp[0][i] = file
          temp[1][i] = os.path.getsize(path + file)
          files_size += temp[1][i]

    # Ordena os arquivos por tamanho
    sizes = sorted(temp[1], reverse=False) # Do menor para o maior
    files = []
    for x in sizes:
      if x > 0:
        i = temp[1].index(x) # Obtem o índice i do menor arquivo em temp[1]
        files.append(temp[0][i]) # Adiciona o nome do menor arquivo pelo índice i
        temp[1][i] = -1 # Atribui um tamanho inválido para o arquivo encontrado
                        # Isso visa evitar repetição da posição de arquivos com
                        # mesmo tamanho. Garante que o arquivo seja selecionado
                        # apenas uma vez na lista.

  return files, files_size

#%% Move arquivos para um diretório informado em path_output
def mv_file(filename:str, path_output:str=f".{SLASH}"):

  tmp_dir = path_output

  if not os.path.isdir(tmp_dir):
    cll()
    print("{:80}".format(f"\rCriando diretório {tmp_dir}"), end="")
    try:
      os.makedirs(name = tmp_dir, exist_ok=True)
    except Exception as E:
      print_erro(f"Erro ao criar {tmp_dir} {E}")

  # Repete verificação do diretório
  if os.path.isdir(tmp_dir):
    if os.path.isfile(filename):
      cll()
      print("{:100}".format(f"\rMovendo {filename} para {tmp_dir} ... "), end="")
      try:
        shutil.move(filename, tmp_dir)
        cll()
        print(f"\r{OK('Arquivo movido com sucesso')}", end="")
        return True
      except Exception as E:
        cll()
        print_erro(f"Erro ao mover {filename}: {E}")
    else:
      cll()
      print_aviso(f"Arquivo {filename} não encontrado.")
  else:
    cll()
    print_aviso(f"{tmp_dir} não encontrado.")

  return False

#%% Copia arquivos para um destino informado em path_output
def cp_file(filename:str, path_output:str=f".{SLASH}"):

    tmp_dir = path_output

    # Separa path_output em nome de diretório e nome de arquivo
    dir_output = os.path.dirname(path_output)
    file_out = os.path.basename(path_output)

    if not file_out:
        file_out = os.path.join(dir_output, os.path.basename(filename))

    if not os.path.isdir(dir_output):
        cll()
        print("{:80}".format(f"\rCriando diretório {dir_output}"), end="")
        try:
            os.makedirs(name = dir_output, exist_ok=True)
        except Exception as E:
            print_erro(f"Erro ao criar {dir_output} {E}")

  # Repete verificação do diretório
    if os.path.isdir(dir_output):
        if os.path.isfile(filename):
            cll()
            print("{:100}".format(f"\rCopiando {filename} para {file_out} ... "), end="")
            try:
                shutil.copy2(filename, file_out)
                cll()
                print(f"\r{OK('Arquivo copiado com sucesso')}", end="")
                return True
            except Exception as E:
                cll()
                print_erro(f"Erro ao copiar {filename}: {E}")
        else:
            cll()
            print_aviso(f"Arquivo {filename} não encontrado.")
    else:
        cll()
        print_aviso(f"{dir_output} não encontrado.")

    return False

#######################
## DELETA UM ARQUIVO ##
#######################
def rm_file(filename:str):

  if os.path.isfile(filename):
    cll()
    print("{:80}".format(f"\rDeletando {filename} ... "), end = "")
    try:
      os.remove(filename)
      print_ok()
      return True
    except Exception as E:
      print_erro(f"Erro ao apagar {filename}: {E}")
  else:
    print_aviso(f"Arquivo {filename} não encontrado.")

  return False
