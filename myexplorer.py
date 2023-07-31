# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 22:31:29 2023

@author: uendel
"""

#%% IMPORTS
import os
import shutil
from myterminal import cll, print_erro, print_aviso, OK
from myconstant import SLASH
from binascii import crc32
from hashlib import sha1, md5

#%% CONSTANTS

#%% Calcula hashes de um arquivo
def crc(file_path):
  with open(file_path, 'rb') as f:
    return hex(crc32(f.read()) & 0xffffffff)
        
def crc_str(s:str, encoding = 'utf-8'):
  return hex(crc32(s.encode(encoding)) & 0xffffffff)

#%% Retorna uma lista de arquivos salvos no formato parquet no diretorio informado
def dir_files(prefix = 'pecas', extension = None, path=f".{SLASH}"):
  
  files_size = 0
  # Todos os arquivos do diretório
  files = [file for file in os.listdir(path=path) if os.path.isfile(path + file)]
  
  # Todos os arquivos com extensão informado em sufix_name
  if extension:
    files = [file for file in files if str(file).split('.')[-1] == extension]
    
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

#%% Move arquivos para o diretório temp
def mv_to_temp(filename:str, path_output:str=f".{SLASH}"):
  
  tmp_dir = path_output
  
  if not os.path.isdir(tmp_dir):
    cll()
    print("{:80}".format(f"\rCriando diretório {tmp_dir}"), end="")
    try:
      os.makedirs(name = tmp_dir, exist_ok=True)
    except Exception as E:
      print_erro(f"Erro ao criar {tmp_dir} {E.args}")

  # Repete verificação do diretório
  if os.path.isdir(tmp_dir):
    if os.path.isfile(filename):
      cll()
      print("{:100}".format(f"\rMovendo {filename} para {tmp_dir} ... "), end="")
      try:
        shutil.move(filename, tmp_dir)
        print(f"\r{OK('Arquivo movido com sucesso')}", end="")
        return True
      except Exception as E:
        print_erro(f"Erro ao mover {filename}: {E.args}")
    else:
      print_aviso(f"Arquivo {filename} não encontrado.")
  else:
    print_aviso(f"{tmp_dir} não encontrado.")

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
      print('Arquivo deletado com sucesso.', end="")
      return True
    except Exception as E:
      print_erro(f"Erro ao apagar {filename}: {E.args}")
  else:
    print_aviso(f"Arquivo {filename} não encontrado.")

  return False


