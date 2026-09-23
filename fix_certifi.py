# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 22:00:33 2026

@author: uendel
"""

import certifi

# 1. Lê os certificados originais da internet do arquivo que você acabou de limpar
with open(certifi.where(), 'r', encoding='utf-8') as f:
    certificados_originais = f.read()

# 2. Lê a cadeia corporativa do STJ baixada pelo Firefox
caminho_stj = r"C:\Users\uendel\Downloads\anaconda-org-chain.pem"
with open(caminho_stj, 'r', encoding='utf-8') as f:
    certificados_stj = f.read()

# 3. Junta os dois com quebras de linha seguras e limpas
certificados_combinados = certificados_originais.strip() + "\n\n" + certificados_stj.strip() + "\n"

# 4. Salva um novo arquivo final seguro na sua pasta de usuário
novo_caminho = r"C:\Users\uendel\conda_cacert_stj.pem"
with open(novo_caminho, 'w', encoding='utf-8') as f:
    f.write(certificados_combinados)

print(f"Sucesso! Arquivo criado em: {novo_caminho}")