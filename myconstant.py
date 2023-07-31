# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 08:53:52 2023

@author: uendel
"""

#%%

import sys


#%% PLATFORM

if sys.platform == 'linux' or sys.platform == 'linux2':
  SLASH = '/'
elif sys.platform == 'win32':
  SLASH = '\\'
