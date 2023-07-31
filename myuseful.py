# -*- coding: utf-8 -*-

def exists(obj_name:str):
  '''
  Retorna True se um objeto existe na memória.

  Parameters
  ----------
  obj_name : str
    obj_name é uma string contendo o nome de um objeto de qualquer tipo.
    Caso o nome do objeto informado exista em locals ou em globals, 
    a função retornará True. Caso não exista, a função retornará 
    False.
    
  Returns
  -------
  bool
    True se o objeto existir.

  '''
  
  if obj_name in locals():
    return True
  elif obj_name in globals():
    return True
  
  return False