# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 23:03:10 2023

@author: uendel
"""
from datetime import datetime
import sys
import os
import myterminal as myt

CHARSET = 'utf-8'

#%%

class MyError(Exception):
  
  def __init__(self, msg = "", obj = None, errorcode:int=0, save_to_log=True, die=False, ExceptionObject = None):
    
    self._object = obj
    self._errorcode = errorcode

    error_msg = f"ERRO: {msg}" if msg else "ERRO: Ocorreu um erro desconhecido."
    obj_msg = f" OBJECT: {self.object_name} | TYPE: {self.object_type}" if self._object else ""
    errorcode_msg = f" | ERRORCODE: {self.errorcode}" if errorcode else ""
    exception_msg = f" | EXCEPTION: {type(ExceptionObject)}: {str(ExceptionObject)}" if ExceptionObject else ""

    self.__msg_err = f"{error_msg} [{obj_msg}{errorcode_msg}{exception_msg}]"

    # A recomendação é que save_to_log esteja True na classe onde ocorre o erro,
    # mas desligado no tratamento geral. Assim, para evitar a perda de log em
    # erros inesperados, save_to_log é True por padrão.
    self._save_to_log = save_to_log
      
      
    myt.print_erro(f"{myt.ERRO('ERRO')} {self.__msg_err}")
    self.save_to_log()

    if die:
      if ExceptionObject:
        raise ExceptionObject

      super().__init__(self.__msg_err)
    else:
      myt.print_ok('\nMoving on...\n')
    
  
  @property
  def object_name(self):
    # check __name__ attribute (functions)
    arg = self._object
    try:
      return arg.__name__
    except AttributeError:
      pass

    for name, value in globals().items():
      if value is arg and not name.startswith('_'):
        return name
      
  @property
  def object_type(self):
    return type(self._object)
  
  @property
  def errorcode(self):
    return f"{self._errorcode:0>5d}"

  @property
  def log_filename(self):
    today = datetime.now().strftime('%Y-%m-%d')
    return f'{today}.log'
  
  def save_to_log(self):
    if self._save_to_log:
      now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
      with open(self.log_filename, 'a+', encoding=CHARSET) as file:
        msg_datetime = f"\n[{now}]"
        file.writelines(['\n', msg_datetime, '\t', ' :: ', self.__msg_err])
        fn = os.path.join(os.getcwd(), file.name)
      
      print(f'Log salvo com sucesso em {fn}')
      
      

class TypeJusticaWebError(MyError):
  def __init__(self, obj, errorcode:int=0):
    msg = "Obrigatório fornecer um parâmetro do tipo JusticaWebConfig."
    super().__init__(msg, obj, errorcode, save_to_log=True, die=False)
    
class TypePecasJusticaError(MyError):
  def __init__(self, obj, errorcode:int=0):
    msg = "Obrigatório fornecer um parâmetro do tipo PecasJustica."
    super().__init__(msg, obj, errorcode, save_to_log=True, die=False)
    
class DataFrameColsError(MyError):
  def __init__(self, obj, errorcode:int=0):
    msg = "Dataframe não existe, está vazio ou incompleto."
    super().__init__(msg, obj, errorcode, save_to_log=True, die=False)

class PathNotFoundError(MyError):
  def __init__(self, obj, errorcode:int=0):
    msg = "Path informado não encontrado."
    super().__init__(msg, obj, errorcode, save_to_log=True, die=False)
    
class NotADirectoryError(MyError):
  def __init__(self, obj, errorcode:int=0):
    msg = "O diretório informado não existe."
    super().__init__(msg, obj, errorcode, save_to_log=True, die=False)
    
class FileNotFoundError(MyError):
  def __init__(self, obj, errorcode:int=0):
    msg = "O arquivo informado já existe."
    super().__init__(msg, obj, errorcode, save_to_log=True, die=False)
    
class FileExistsError(MyError):
  def __init__(self, obj, errorcode:int=0):
    msg = "O arquivo informado já existe."
    super().__init__(msg, obj=obj, errorcode=errorcode, save_to_log=True, die=False)
    
class ServiceExecuteError(MyError):
  def __init__(self, msg, obj, errorcode:int=0, ExceptionObject:Exception=None):
    msg = f"ERRO AO EXECUTAR SERVIÇO: {msg}"
    super().__init__(msg, obj=obj, errorcode=errorcode, save_to_log=True, die=False, ExceptionObject=ExceptionObject)


class DatabaseLoadError(MyError):
  def __init__(self, msg, obj, errorcode:int=0, ExceptionObject:Exception=None):
    msg = f"ERRO AO CARREGAR DADOS: {msg}"
    super().__init__(msg, obj=obj, errorcode=errorcode, save_to_log=True, die=False, ExceptionObject=ExceptionObject)

class DatabaseSaveError(MyError):
  def __init__(self, msg, obj, errorcode:int=0, ExceptionObject:Exception=None):
    msg = f"ERRO AO SALVAR DADOS: {msg}"
    super().__init__(msg, obj=obj, errorcode=errorcode, save_to_log=True, die=False, ExceptionObject=ExceptionObject)

class RecordNotFound(MyError):
  def __init__(self, msg, obj, errorcode:int=0, die=False, ExceptionObject:Exception=None):
    msg = f"REGISTRO NÃO ENCONTRADO: {msg}"
    super().__init__(msg, obj=obj, errorcode=errorcode, save_to_log=True, die=die, ExceptionObject=ExceptionObject)

class ValueNotFound(MyError):
  def __init__(self, msg, obj, errorcode:int=0, die=False, ExceptionObject:Exception=None):
    msg = f"VALOR OBRIGATÓRIO NÃO ENCONTRADO: {msg}"
    super().__init__(msg, obj=obj, errorcode=errorcode, save_to_log=True, die=die, ExceptionObject=ExceptionObject)

class InconsistentDataError(MyError):
  def __init__(self, msg, obj, errorcode:int=0, die=False, ExceptionObject:Exception=None):
    msg = f"DADOS INCONSISTENTES: {msg}"
    super().__init__(msg, obj=obj, errorcode=errorcode, save_to_log=True, die=die, ExceptionObject=ExceptionObject)


class ParsingError(MyError):
  def __init__(self, msg, obj, errorcode:int=0, die=False, ExceptionObject:Exception=None):
    msg = f"ERRO DURANTE ANÁLISE DO OBJETO: {msg}"
    super().__init__(msg, obj=obj, errorcode=errorcode, save_to_log=True, die=die, ExceptionObject=ExceptionObject)


class FutureDateNotAllowed(MyError):
  def __init__(self, date:str, errorcode: int = 0, die=False):
    msg = f"ERRO: {str(date)} é futuro. Valor não permitido."
    super().__init__(msg, obj=date, errorcode=errorcode,
                     save_to_log=True, die=die, ExceptionObject=ValueError(msg))
