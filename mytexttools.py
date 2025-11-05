#!/usr/bin/env python3
#! python3
# -*- coding: utf-8 -*-
from enum import Enum, unique
import regex # pip install regex
import re

class StopWords_PtBr(Enum):
  
  # [w.strip() for w in ''.split(',')]
  # Preposições  
  essenciais = [w.strip() for w in 'a, ante, após, até, com, contra, de, do, dos, da, das, desde, em, no, nos, na, nas, entre, para, per, perante, por, sem, sob, sobre, trás'.split(',')]
  acidentais = [w.strip() for w in 'afora, como, conforme, consoante, durante, exceto, mediante, menos, salvo, segundo, visto'.split(',')]
  
  # Conjunções
  aditivas     = [w.strip() for w in 'e, mas ainda, mas também, nem'.split(',')]
  adversativas = [w.strip() for w in 'contudo, entretanto, mas, não obstante, no entanto, porém, todavia'.split(',')]
  alternativas = [w.strip() for w in 'já, ou, ora, quer'.split(',')]
  conclusivas  = [w.strip() for w in 'assim, então, logo, pois, por conseguinte, por isso, portanto'.split(',')]
  explicativas = [w.strip() for w in 'pois, porquanto, porque, que'.split(',')]
  
  # Artigos
  definidos   = [w.strip() for w in 'o, os, a, as'.split(',')]
  indefinidos = [w.strip() for w in 'um, uns, uma, umas'.split(',')]
  
  # Outros
  simbolos = [w.strip() for w in 'n, nº, n., no.'.split(',')]
  
  
  @classmethod
  def stopwords(self):
    words = StopWords_PtBr
    result = []
    for w in words:
      result += w.value
      
    return result

class Symbols(Enum):
  acute = "áéíóúÁÉÍÓÚýÝ"
  grave = "àèìòùÀÈÌÒÙ"
  circunflex = "âêîôûÂÊÎÔÛ"
  tilde = "ãõÃÕñÑ"
  umlaut = "äëïöüÄËÏÖÜÿ"
  cedil = "çÇ"
  
  @classmethod
  def symbols(self):
    accents = Symbols
    result = ''
    for s in accents:
      result += s.value
      
    return result
      
#+ self.grave + self.circunflex + self.tilde + self.umlaut + self.cedil

class NudeSymbols(Enum):
  acute = "aeiouAEIOUyY"
  grave = "aeiouAEIOU"
  circunflex = "aeiouAEIOU"
  tilde = "aoAOnN"
  umlaut = "aeiouAEIOUy"
  cedil = "cC"

class AlphaNum(Enum):
  alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
  numeric = "0123456789"
  period = ".?!"
  semiperiod = ";:"
  #remove = str(r".,/\{\}[]@#$%&*()-_=+§:;?ªº\'\"° ")

AccentsType = ["´","`","^","~","¨","ç"]
SpecialsType = str(r".,/\{\}[]@#$%&*()-_=+§:;?ªº\'\"° ")

class Mapping():
  def __init__(self):
    self._map = {} # {'word':{'count':0, 'index':[0,0,0,0]}} # index = row()

  @property
  def map(self):
    return self._map
  
  @map.setter
  def map(self, value={'word':'', 'index':0}):
    word = value['word']
    index = value['index']
    if word in self._map:
      self._map[word]['count'] += 1
      self._map[word]['index'] += [index]
    else:
      self._map[word] = {'count': 1, 'index': [index]}

    self._map[word]['index'] = sorted(list(set(self._map[word]['index'])))
    return self._map

  def count(self, word:str):
    if word in self._map:
      return self._map[word]['count']
    else:
      return 0

  def index(self, word:str):
    if word in self._map:
      return self._map[word]['index']
    else:
      return []

mapped_accents = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c'
    }

# Adiciona as versões maiúsculas ao dicionário existente
mapped_accents.update({k.upper(): v.upper() for k, v in mapped_accents.items()})

##################################################################################
def rm_accent(text:str):
    
    if type(text) == str:
        for x in Symbols:
            return text.translate(str.maketrans(x.value, NudeSymbols[x.name].value))
    elif type(text) == list:
        result = [rm_accent(s) for s in text]
        return result

def remove_mapped_accents(text:str):
    return text.translate(str.maketrans(mapped_accents))

##################################################################################
def lower(text:str):
  ''' lower(text: str)
      Transform all strings in lowercase from string or list of strings
  '''
  if type(text) == str:
    return text.lower()
  elif type(text) == list:
    return [lower(s) for s in text]
  else:
    return text

def upper(text:str):
  ''' lower(text: str)
      Transform all strings in lowercase from string or list of strings
  '''
  if type(text) == str:
    return text.upper()
  elif type(text) == list:
    return [upper(s) for s in text]
  else:
    return text

def normal(text:str):
  return text

@unique
class EnumCase(Enum):
  lowercase  = -1;
  normalcase =  0;
  uppercase  =  1;
  
def convert_to_case(enum_case:EnumCase):
  match enum_case:
    
    case EnumCase.lowercase:
      return lower
    
    case EnumCase.normalcase:
      return normal
    
    case EnumCase.uppercase:
      return upper
    

##################################################################################
from unicodedata import normalize
def normalize_text(text:str, charcase:EnumCase=EnumCase.normalcase):
  if type(text) == str:
    return normalize('NFKD', convert_to_case(charcase)(text)).encode('ASCII', 'ignore').decode('ASCII')
  elif type(text) == list:
    return [normalize_text(word, charcase) for word in text]

##################################################################################
def pieces(text:str, sep=" "):
  result = {}
  if type(text) == str:
    result[text] = {}
    index = 0
    for piece in text.split(sep):
      if not piece.strip() == "":
        result[text][index] = piece
        try:
          index = text.index(sep, index + 1) + 1
        except:
          continue

  return result

##################################################################################
def sentences(text:str):
  result = {}
  if type(text) == str:
    result[text] = {} # Text as a key
    index = 0
    for i in range(0, len(text), 1):
      if text[i] in AlphaNum.period.value:
        period = text[index:i+1]
        if period.strip() != "":
          result[text][index] = period
        index = i + 1

  return result

##################################################################################
def word_count(text:str):
  result = {}

  def count(s):
    result[s] = 1 if not s in result.keys() else result[s] + 1

  if type(text) == str:
    for s in text.split():
      count(s)
  elif type(text) == list:
    for s in text:
      count(s)

  return result


def apply_regex(regex, texto):
  r"""
  Aplica um padrão regex a um texto e retorna os grupos capturados.

  Args:
  regex (str): O padrão de expressão regular a ser aplicado.
  texto (str): O texto no qual o regex será aplicado.

  Returns:
  tuple: Uma tupla contendo os grupos capturados pelo regex.
         Retorna None se nenhuma correspondência for encontrada.
         
  
  # Exemplo de uso do método
  regex = '(nrm:)(\D*)(_)(\d*)(_)(\d*)'
  texto = 'nrm:lei_10826_03_processo_n_0051458-1320148060167'
  
  # Aplica o regex ao texto
  resultado = apply_regex(regex, texto)
  
  # Imprime o resultado
  # No caso, uma tupla com os grupos ('nrm:', 'lei', '_', '10826', '_', '03')
  print(resultado)
  
  # Se houver resultado, imprime o resultado concatenado
  # No caso, nrm:lei_10826_03
  if resultado:
    print(''.join(resultado))
  
  """
  # Usa re.search() para encontrar a primeira ocorrência do padrão no texto
  matching = re.search(regex, texto)
  # Verifica se uma correspondência foi encontrada
  if matching:
    # Se encontrada, retorna uma tupla com todos os grupos capturados
    return matching.groups()
  # Se nenhuma correspondência for encontrada, retorna None
  return None


#%%
# TODO: Permitir que old e new sejam str ou list e percorridas par a par
def replace(text:str, old, new=''):
    result = ""
    if type(text) == str:
        #result = text.replace(old, new)
        result = regex.sub(old, new, text)
    elif type(text) == list:
      result = [replace(s, old, new) for s in text]
    else:
      result = text
    
    return result

#%%
##################################################################################
def sanitize_char(text:str, new_char=' '):
  ''' sanitize_char(text:str)
      Retorna o texto apenas com caracteres alfanuméricos e espaço.
  '''
  result = ""
  if type(text) == str:
    for c in text:
      if c.isalnum() or c.isspace():
        result += c
      else:
        result += str(new_char)

    return result
  elif type(text) == list:
    result = [sanitize_char(s, new_char) for s in text]
  else:
    result = text
  
  return result

##################################################################################
def words(text:str):
  result = []
  if type(text) == str:
    result = sanitize_char(text).split()
  elif type(text) == list:
    result = [sanitize_char(s).split() for s in text]

  return result

##################################################################################
from nltk.tokenize import word_tokenize
def tokenize(text:str):
  return word_tokenize(text)

##################################################################################
from nltk.probability import FreqDist
import pandas as pd
def frequency(words:[]):
  fdist = FreqDist(words)
  count_frame = pd.DataFrame(fdist, index = [0]).T
  count_frame.columns = ['count']
  return count_frame

