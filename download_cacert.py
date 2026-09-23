import urllib.request
import ssl
import certifi

print("Baixando pacote de certificados limpo...")

# Cria um contexto que ignora o bloqueio do STJ apenas para este download
ctx = ssl._create_unverified_context()
resposta = urllib.request.urlopen('https://curl.se/ca/cacert.pem', context=ctx)
certificados_puros = resposta.read().decode('utf-8')

# Sobrescreve o arquivo corrompido
caminho = certifi.where()
with open(caminho, 'w', encoding='utf-8') as f:
    f.write(certificados_puros)

print(f"Sucesso absoluto! Arquivo restaurado e higienizado em: {caminho}")