# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 01:39:52 2023

@author: uendel
"""

import ast
from cryptography.fernet import Fernet # pip install cryptography

class Key():
# =============================================================================
#   Realiza criptografia/decriptografia simples de qualquer coisa usando
#   uma chave fixa. Há possibilidade de setar uma chave diferente por meio do
#   método estático key. Recomenda-se que a chave esteja no padrão Fernet.
#
#   Para inicializar uma instância com uma nova chave aleatória:
#   k = crypto.Key.init_with_key(crypto.Key.new_key())
#
#   Para inicializar uma instância com uma chave fixa conhecida:
#   k = crypto.Key.init_with_key(b'0DeAIQsLDgvm2M8SXctog9OrYtIB2y-xC8cFvPX8KAk=')
#
#   IMPORTANTE: a chave Fernet deve ser 32 url-safe  base64-encoded bytes
# =============================================================================

  KEY = b'8bp4BMbuS3nrpDl0fN8aFaJnxvELAJW3nhalHoQX908='

  def __init__(self, key):
    self.KEY = key

  @classmethod
  def init_with_key(cls, key = KEY):
    if key != Key.KEY:
      Key.KEY = key
      
    return cls(Key.KEY)
  
  @staticmethod
  def fixed_key():
    return Key.KEY
      
  
  @staticmethod
  def new_key():
    return Fernet.generate_key()
  
  @staticmethod
  def encrypt(anything):
    if isinstance(anything, str):
      byte_string = anything.encode()
    elif isinstance(anything, bytes):
      byte_string = anything
    else:
      byte_string = str(anything).encode()
      
    fernet = Fernet(Key.fixed_key())
    return fernet.encrypt(byte_string)
  
  @staticmethod
  def encrypt_to_textfile(anything, filename:str):
    encrypted = Key.encrypt(anything)
    
    filename = '.'.join(filename.split('.')[:-1]) + '.k'
    
    with open(filename, "w") as text_file:
      text_file.write(encrypted.decode())
    text_file.close()
    
  @staticmethod
  def decrypt(encrypted:str):
    if isinstance(encrypted, str):
      string = encrypted
    elif isinstance(encrypted, bytes):
      string = encrypted.decode()
    else:
      raise TypeError("Parameter 'encrypted' must be str type or bytes type")
      
    fernet = Fernet(Key.fixed_key())
    decrypted = fernet.decrypt(string)
    
    try:
      # Tenta retornar o texto decriptado como um objeto ou estrutura de dados
      result = ast.literal_eval(decrypted.decode())
    except SyntaxError:
      # Retorna o texto decriptado como uma string
      result = decrypted.decode()
    except Exception:
      # Retorna o texto tal como foi decriptado
      result = decrypted
    
    return result
    
  @staticmethod
  def decrypt_from_textfile(filename:str):

    with open(filename, "r") as text_file:
      encrypted = text_file.read()
    text_file.close()
    
    return Key.decrypt(encrypted=encrypted)
