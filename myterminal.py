# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 20:35:19 2023

@author: uendel
"""

import os
from console import fg, bg, fx
from random import randint

import tkinter as tk
from tkinter import font as tkfont
import shutil


#%% CONSTANTES PARA SAÍDA DE TEXTO DO TERMINAL
# TERMINAL_SIZE = os.get_terminal_size

ERRO = fg.yellow + fx.bold + bg.red
AVISO = fg.red + fx.bold + bg.yellow
OK = fg.green + fx.bold
INFO = fg.cyan + fx.bold

BLUE = fg.black + fx.bold + bg.blue
MAGENTA = fg.black + fx.bold + bg.magenta
CYAN = fg.black + fx.bold + bg.cyan
YELLOW = fg.black + fx.bold + bg.yellow
GREEN = fg.black + fx.bold + bg.green
RED = fg.black + fx.bold + bg.red
BLACK = fg.black + fx.bold + bg.white
GRAY = fg.black + fx.bold + bg.gray

RESET = bg.black + fg.white

# CLEAR_LINE_MSG = f"\r{' ' * max_cols()}"

def max_chars_font(font_family='Courier', font_size=12):
    # Cria uma janela temporária
    root = tk.Tk()
    root.withdraw()  # Esconde a janela

    # Obtém a resolução da tela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()

    # Cria uma fonte padrão
    fonte = tkfont.Font(family=font_family, size=font_size)

    # Calcula a largura média de um caractere
    largura_caractere = fonte.measure(' ')

    # Calcula o número máximo de caracteres por linha
    max_cols = largura_tela // largura_caractere
    max_rows = altura_tela // font_size

    # print(f"Resolução da tela: {largura_tela}x{altura_tela}")
    # print(f"Largura média de um caractere: {largura_caractere:.2f} pixels")
    # print(f"Número máximo de caracteres por linha: {max_caracteres}")

    # Fecha a janela temporária
    root.destroy()

    return max_cols, max_rows

try:
    MAX_H_CHARS, MAX_V_CHARS = max_chars_font('Consolas', 16)
except Exception as e:
    # Fallback para ambiente headless (sem display)
    MAX_H_CHARS, MAX_V_CHARS = (80, 24)  # Valores padrão
    import logging
    logging.warning(f"Modo headless detectado: usando valores padrão de terminal")

#%% Configurações do terminal
def max_cols():
    try:
        return os.get_terminal_size().columns
    except:
        try:
            return shutil.get_terminal_size().columns
        except:
            return MAX_H_CHARS

def max_lines():
    try:
        return os.get_terminal_size().lines
    except:
        try:
            return shutil.get_terminal_size().lines
        except:
            return MAX_V_CHARS

# clear line
def cll(size:int=0):
  #print(f"\r{' ' * size}", end="")
  # print('\b' * size, end="")
  size = max_cols() if size == 0 else size
  print(f"\r{' ' * size}", end="\r")
  
def clear_line_msg():
  return f"\r{' ' * max_cols()}"


#%% Funções que retornam mensagens formatadas no terminal
def print_erro(msg, end = ''):
  formato = "{:<" + str(len(msg)) + "}"
  # formato = "{:>240}"
  # cll()
  print(formato.format(f"\n\U000026D4 {ERRO('ERRO')} {msg}"),
        end=' \U000026D4 \n' if end == '' else f' \U000026D4 {end}')

def print_aviso(msg, end = ''):
  formato = "{:<" + str(len(msg)) + "}"
  # formato = "{:80}"
  # cll()
  print(formato.format(f"\n\U000026A0 {AVISO('AVISO')} {msg}"),
        end=' \U000026A0 \n' if end == '' else f' \U000026A0 {end}')

def print_ok(msg="OK", end=""):
  formato = "{:<" + str(len(msg)) + "}"
  # formato = "{:>" + str(len(msg)) + "}"
  # cll()
  print(formato.format(f"{OK(msg)}"), 
        end='\n' if end == '' else end)

def print_info(msg="INFO", end=" "):
  formato = "{:<" + str(len(msg)) + "}"
  r = clear_line_msg() if len(msg) >= max_cols() else ''
  # formato = "{:<" + str(len(msg)) + "}"
  # cll()
  print(formato.format(f"{r}{INFO(msg)}"), end=end)


#%% GAUGES AND BARS
def gauge(i, max = 100, steps = 10):
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
  "vbar": ['▁','▂','▃','▄','▅','▆','▇','█','▀','¯'], # i % 10
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
