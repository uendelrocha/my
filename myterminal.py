# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 20:35:19 2023

@author: uendel
"""

import os
from console import fg, bg, fx
from random import randint


#%% CONSTANTES PARA SAÍDA DE TEXTO DO TERMINAL
TERMINAL_SIZE = os.get_terminal_size

ERRO = fg.yellow + fx.bold + bg.red
AVISO = fg.red + fx.bold + bg.yellow
OK = fg.green + fx.bold
INFO = fg.cyan + fx.bold

CLEAR_LINE_MSG = f"\r{' ' * TERMINAL_SIZE()[0]}"

#%% Configurações do terminal
def max_cols():
  return TERMINAL_SIZE()[0] * 2

def max_lines():
  return TERMINAL_SIZE()[1]

# clear line
def cll(size = max_cols()):
  print(f"\r{' ' * size}", end="")

#%% Funções que retornam mensagens formatadas no terminal
def print_erro(msg, end = ''):
  cll()
  print("{:>210}".format(f"\r\U000026D4 {ERRO('ERRO')} {msg}"),
        end='\U000026D4 \r\n' if end == '' else f'\U000026D4 {end}')

def print_aviso(msg, end = ''):
  cll()
  print("{:80}".format(f"\r\U000026A0 {AVISO('AVISO')} {msg}"),
        end='\U000026A0 \r' if end == '' else f'\U000026A0 {end}')

def print_ok(msg="OK", end=""):
  cll()
  print("{:>210}".format(f"{OK(msg)}"), end=end)

def print_info(msg="INFO", end=""):
  cll()
  print("{:<120}".format(f"{INFO(msg)}"), end=end)


#%% GAUGES AND BARS
def gauge(i, max = 100, steps = 20):
  percent = round((i / max) * 100, 4)
  step = int(steps * percent // 100)
  return f"{i}/{max} {percent:0.2f}% {'■' * step:⬚<{steps}}"

def slide_bar(i, steps = 10, fill_char = '■', step_char = '⬚', slide = True):
  bar = list(step_char * steps)
  if slide:
    bar[i % steps] = fill_char
  else:
    bar[0:(i % steps) + 1] = "■" * ((i % steps) + 1)
    #bar[0:(i + 1) % steps] = fill_char * (i % steps)

  bar = "".join(bar)
  return f"{bar:{steps}}" #f"{bar:<{steps}}".format(bar)

# for i in range(11):
#     caixa = list("⬚" * 10)
#     caixa[0:i % 10 + 1] = "■" * (i%10+1)
#     caixa = "".join(caixa)
#     print(f'{caixa}', end=f"{i}")
#     time.sleep(0.5)


propellers = {
  "slash":['|','/','—','\\'],
  "dotbar":['░', '▒', '▓', '█'], # ASSCII: 176, 177, 178, 219
  "vslice": ['_','▄','■', '▀', '¯'], # ASCII: _, 220, 254, 223, 254, 238
  "vbar": ['▁','▂','▃','▄','▅','▆','▇','█','■','▀','¯'], # i % 10
  'hbar': ['▏','▎','▍','▋','▊','▉'], # i % 5
  'sonar': ['◯','⬤','●','•','○','◌'], # i % 3
  "dash": ['_','‗','═','¯­­­'], # i % 4
  "squares": ['◳','◲','◱','◰'],
  "pipes": ['╗','╝','╚','╔'],
  "pizza": ['◷','◶','◵','◴'],
  "circles": ['◦','○','◌','◯','◌','○'],
  "slide_bar": slide_bar,
              }

def propeller():
  return propellers[list(propellers.keys())[randint(0, len(propellers)-1)]]
