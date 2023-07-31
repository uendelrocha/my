# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 23:03:10 2023

@author: uendel
"""

from myterminal import ERRO

#%%

class MyError(Exception):
  
  def __init__(self, msg = "", obj = None, errorcode:int=0):
    super().__init__(f"{ERRO('ERRO')} {msg} [OBJETO: {self.name_of_object(obj)} | TYPE: {type(obj)} | ERRORCODE: {errorcode:0>5d}]")
      
  def name_of_object(self, arg):
    # check __name__ attribute (functions)
    try:
      return arg.__name__
    except AttributeError:
      pass

    for name, value in globals().items():
      if value is arg and not name.startswith('_'):
        return name
  

class TypeJusticaWebError(MyError):
  
  def __init__(self, msg = "", obj = None, errorcode:int=0):
    super().__init__("Você deve fornecer um parâmetro do tipo JusticaWebConfig", obj, errorcode)

class DataFrameColsError(MyError):

  def __init__(self, msg = "", obj = None, errorcode:int=0):
    super().__init__("Dataframe não existe, está vazio ou incompleto.", obj, errorcode)

class PathNotFoundError(MyError):
  def __init__(self, msg = "", obj = None, errorcode:int=0):
    super().__init__("Path informado não encontrado.", obj, errorcode)

