# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 01:39:52 2023

@author: uendel
"""

import ast # Abstract Syntax Trees
from cryptography.fernet import Fernet # pip install cryptography
from typing import Any

FIXED_KEY = b'8bp4BMbuS3nrpDl0fN8aFaJnxvELAJW3nhalHoQX908='

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

  """
    FAQ
  
    1. Como criptografar uma chave segura aleatória em um arquivo?
    R. Para criptografar uma chave segura aleatória, basta criar um arquivo .k
       com os seguintes comandos:
     
          from mykeychain import Key, FIXED_KEY
          Key.encrypt_to_textfile(Key.new_key(), 'key.k')
    
    2.  Como usar uma chave anteriormente salva em um arquivo criptografado?
        Para usar a chave salva em um arquivo criptografado em uma nova criptografia, 
        deve-se primeiro decriptografar a chave no arquivo para um objeto do tipo Key.
        Se o arquivo foi criptografado com a chave fixa, deve-se usar o seguinte código:
       
          # Instancia um objeto Key com uma chave em um arquivo criptografado
          key = Key.init_with_key(Key.decrypt_from_textfile('key.k', key=FIXED_KEY))
     
        De posse do objeto com a chave, pode-se utilizá-lo para criptografar/decriptografar qualquer informação ou arquivo:
     
          # Criptografando um arquivo com a chave no objeto:
          key.encrypt('Este é um teste que retorna este texto criptografado por um objeto key')
          
          # Criando um dicionário e criptografando para um arquivo em disco com o objeto key
          my_dic = {'Uendel': {'email': 'uendelrocha@gmail.com', 'passwd':'123456'}}
          key.encrypt_to_textfile(my_dic, 'my_dic.k')
          f = open('my_dic.k', 'r')
          encrypted_dic = f.read()
          print(encrypted_dic)
          
          # Decriptografando o dicionário
          txt_dic = key.decrypt(encrypted_dic)
          print(type(txt_dic), txt_dic) # Deve retornar: <class 'dict'> {'Uendel': {'email': 'uendelrocha@gmail.com', passwd':'123456'}}
          
          # Usando Key para carregar o dicionário salvo em arquivo criptografado
          txt_dic = key.decrypt_from_textfile('my_dic.k')
          print(txt_dic)
          
    3.  Qual é a recomendação para usar a criptografia em tempo de execução?
        Recomenda-se que as informações de chave e senha sejam o mais voláteis possível. Para isso, recomenda-se que
        os objetos Key sejam instanciados e destruídos no contexto de seu uso mais estrito. Recomenda-se que os valores
        das chaves e informações decriptografadas sensíveis NÃO sejam guardados em variáveis, mas retornados como parâmetros e
        destruídos imediatamente após o objetivo de seu uso ter sido alcançado.
        
        Por exemplo, suponhamos que o usuário e a senha de um serviço estejam em um dicionário criptografado em arquivo.
        Em vez de carregar a informação decriptografada para uma variável em memória, recomenda-se utilizar a informação
        desejada diretamente no parâmetro do serviço. Por exemplo, suponha-se que o método connect do serviço my_srvc
        tenha como parâmetros usuário e senha guardados em um arquivo my_srvc.k criptografado por uma chave criptografada
        em um arquivo key.k:
        
          # Criando o procedimento de conexão ao serviço
          def my_srvc(user:str=None, passwd:str=None):
            print(f'Connecting {user} to my_srvc... ', end='')
            if passwd:
              print('OK')
              return b'CONEXAO{<database.connection>}'
            else:
              print('FAILED')
              return None
          
          from mykeychain import Key, FIXED_KEY
          
          # Criando, criptografando e salvando uma chave aleatória em key.k
          Key.encrypt_to_textfile(Key.new_key(), 'key.k', key = FIXED_KEY)
          
          # Criando e criptografando um dicionário com usuário e senha (exemplo)
          dic = {'usuario': 'uendelrocha@gmail.com', 'senha':'123456'}
          Key.init_with_key(Key.decrypt_from_textfile('key.k', key = FIXED_KEY)).encrypt_to_textfile(dic, 'my_srvc.k')

        A decriptografia poderia ocorrer de duas formas:
                    
          # 1a FORMA: Guardando os dados em variáveis locais (não recomendado)
          # Nesta forma, as variáveis usuário e senha continuam acessíveis após a execução do serviço
          srvc_key = Key.decrypt_from_textfile('key.k', key = FIXED_KEY)
          key = Key.init_with_key(srvc_key)
          dic = key.decrypt_from_textfile('my_srvc.k')
          usuario, senha = dic['usuario'], dic['senha']
          my_srvc(user=usuario, passwd=senha)
          print(usuario, senha)
          
          # 2a FORMA: Usando uma função local que lê o arquivo criptogrado e executa o método de conexão (RECOMENDADO)
          # Essa forma não armazena credenciais em variáveis locais, apenas a conexão retornada pelo método.
          # Isso garante menos exposição das credenciais no código.
          def get_mysrvc_credential():
            from mykeychain import Key
            dic = Key.init_with_key(Key.decrypt_from_textfile('key.k', key = FIXED_KEY)).decrypt_from_textfile('my_srvc.k')
            return dic['usuario'], dic['senha']
        
          conexao = my_srvc(*get_mysrvc_credential())
          print(conexao)
        
      
  """

  KEY = None

  @staticmethod
  def new_key():
    return Fernet.generate_key()

  def __init__(self):
    if type(self.KEY) is type(None):
      self.KEY = self.new_key()

  @classmethod
  def init_with_key(cls, key):
    try:
      cls.encrypt('TESTING KEY', key)
      obj = cls()
      obj.KEY = key
    except Exception as E:
      raise E

    # return cls(cls.KEY)
    # return cls()
    return obj

  @staticmethod
  def check_key(key):
    # Se key foi informada, retorna key
    if not type(key) is type(None):
      result = key
    # Se a chave não foi informada e o objeto não foi instanciado com uma chave, retorna a chave fixa
    elif type(Key.KEY) is type(None):
      result = FIXED_KEY
    # Se a chave não foi informada e o objeto foi instanciado com uma chave, retorna a chave do objeto
    else:
      result = Key.KEY
    
    return result

  
  @staticmethod
  def encrypt(anything, key = None):
    if isinstance(anything, str):
      byte_string = anything.encode()
    elif isinstance(anything, bytes):
      byte_string = anything
    else:
      byte_string = str(anything).encode()
      
    #fernet = Fernet(Key.fixed_key())
    fernet = Fernet(Key.check_key(key))
    return fernet.encrypt(byte_string)
  
  @staticmethod
  def encrypt_to_textfile(anything, filename:str, key = None):
    encrypted = Key.encrypt(anything, key)
    
    filename = '.'.join(filename.split('.')[:-1]) + '.k'
    
    with open(filename, "w") as text_file:
      text_file.write(encrypted.decode())
    text_file.close()
    
  @staticmethod
  def decrypt(encrypted:str|bytes, key = None) -> Any:
    if isinstance(encrypted, str):
      string = encrypted
    elif isinstance(encrypted, bytes):
      string = encrypted.decode()
    else:
      raise TypeError("Parameter 'encrypted' must be str type or bytes type")
      
    fernet = Fernet(Key.check_key(key))
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
  def decrypt_from_textfile(filename:str, key = None) -> Any:

    with open(filename, "r") as text_file:
      encrypted = text_file.read()
    text_file.close()
    
    return Key.decrypt(encrypted=encrypted, key=key)

  # def decrypt_from_textfile(self, filename:str) -> Any:
  #   return Key.decrypt_from_textfile(
  #     filename=filename,
  #     key = self.KEY
  #     )

  @staticmethod
  def encrypt_2f(s:str, key_filename:str, key = None) -> bytes:
    factor_0 = key if key else FIXED_KEY
    factor_1 = Key.decrypt_from_textfile(key_filename, key=factor_0)
    
    # O fator 2 será a chave criptografada virtualmente desconhecida utilizada exclusivamente para encriptar o texto criptografado
    # Cada vez que o texto é encriptado, uma nova chave desconhecida é gerada para servir como segundo fator
    # O segundo fator serve para criptografar dados sensíveis dentro de um contexto de dados já criptografados.
    # Por exemplo, a chave para o segundo fator pode ser guardada junto com parâmetros de conexão representando o usuário e a senha
    factor_2 = Key.encrypt(Key.new_key(), key = factor_1)
    
    bytes_1f = Key.encrypt(s, key = factor_1)
    bytes_2f = Key.encrypt(bytes_1f, key = Key.decrypt(factor_2, key = factor_1))

    return factor_2, bytes_2f
  
  @staticmethod
  def decrypt_2f(factor_2:bytes, bytes_2f:bytes, key_filename:str, key = None) -> Any:
    factor_0 = key if key else FIXED_KEY
    factor_1 = Key.decrypt_from_textfile(key_filename, key=factor_0)
    
    bytes_1f = Key.decrypt(bytes_2f, key = Key.decrypt(factor_2, key = factor_1))
    
    return Key.decrypt(bytes_1f, key = factor_1)
