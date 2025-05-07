import copy
import sys, os
import locale
import pandas as pd

import string
from datetime import datetime, date

from itertools import product
from urllib import response
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from pyperclip import copy, paste

import chardet

import re
import regex # pip install regex

# Regex para capturar os metadados
LEI_REGEX     = r"(?P<lei>^(?P<lei_tipo>\b(?:DECRETO-LEI|DECRETO|LEI(?: COMPLEMENTAR| DELEGADA)?|CONSTITUI[ÇC][ÃA]O))\b\s+(?:n(?:[.°ºo]|o\.|úmero)?)\s+(?P<lei_num>[0-9.]*)\s*(?:,?\s*(?:de))\s*(?P<lei_data>.*?\s*(?P<lei_ano>(?:[0-9\s]{1,2}\d{3}))))"
REVOGADA_REGEX  = r"(?P<revogada>^(Revogad[ao])(.*)(\n))"

# Regex para capturar os dispositivos legais
ARTIGO_REGEX  = r"(?P<art>^(?P<art_no>Art. \d*)(\w*\W*)(?P<art_text>.*)(\n))"
CITACAO_REGEX = r"(?P<cit>^(\")(\w*|\W)*(\"|\(NR\))$)"
PARAGR_REGEX  = r"(?P<par>^(?P<par_no>(§\s*\d*)|(Par[áa]grafo [ÚúUu]nico))(\w*\W*\s*)(?P<par_text>.*)(\n))"
INCISO_REGEX  = r"(?P<inc>^(?P<inc_no>\b^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\b)(\. *|\W)(?P<inc_text>.+)(\n))"
ALINEA_REGEX  = r"(?P<aln>^(?P<aln_no>[a-zA-Z]+\)\s*)(?P<aln_text>.*)(\n))"
ITEM_REGEX    = r"(?P<itm>^(?P<itm_no>[1-9]+\W\s+)(?P<itm_text>.*)(\n))"

# Regex para capturar o local e a data (metadados)
LOCAL_REGEX   = r"(?P<local_data>^(?P<local>\b(?:Salvador|Rio de Janeiro|Bras[íi]lia)\b)(?:[ ,]+)(?:DF|RJ|BA)?(?:[., ]+)(?P<data>(?P<local_data_dia>\d{1,2})[ oºde]{4,5}(?P<local_data_mes>\b(?:janeiro|fevereiro|mar(?:ç|c)o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\b)[de ]{4,5}(?P<local_data_ano>[0-9][. ]{0,1}[0-9]{3,4})))"

# Regex para capturar o aviso de publicacao
PUBLICACAO_REGEX = r"(?im)^\s*(?P<publicacao>Este\s+texto\s+n[aã]o\s+subst.*?\s+o(?:\s+original)?\s+publicado.*(?:CLBR|D\.?O\.?U\.?).*?$)"
CLBR_DATA_REGEX  = r"(?i)CLBR.*?(?P<clbr_data>\d{1,2}[oº°]? ?\.\d{1,2}\.\d{4})"
DOU_DATA_REGEX   = r"(?i)D\.?O\.?U\.?.*?(?P<dou_data>\d{1,2}[oº°]? ?\.\d{1,2}\.\d{4})"

DATA_EXTENSO_REGEX = r'(?im)(?P<data_extenso>(?P<data_ext_dia>\d{1,2})[ oºde]{4,5}(?P<data_ext_mes>\b(?:janeiro|fevereiro|mar(?:ç|c)o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\b)[de ]{4,5}(?P<data_ext_ano>[0-9][. ]{0,1}[0-9]{3,4}))'
DATA_CURTA_REGEX = r'(?im)\b(?P<data_curta>(?P<data_curta_dia>\d{1,2})[oº°]? ?[.\-/](?P<data_curta_mes>\d{1,2})[.\-/](?P<data_curta_ano>[0-9][ .]?\d{3}))\b'

METADADOS_REGEX_PAT = '|'.join([r'(?im)' + LEI_REGEX, REVOGADA_REGEX, LOCAL_REGEX])
DISPOSITIVO_REGEX_PAT = '|'.join([r'(?m)' + ARTIGO_REGEX, CITACAO_REGEX, PARAGR_REGEX, INCISO_REGEX, ALINEA_REGEX, ITEM_REGEX])

IGNORE_REGEX     = r"(?im)(?P<ignorado>^\b(?:Texto(?: compilado| original| para impressão))\b)"
FIRST_WORD_REGEX = r"^\s*(\w+)" # A palavra é alfanumérica
LAST_WORD_REGEX  = r"(\w+)\s*$" # A palavra é alfanumérica

CHARS_PUNCT_START = '(<[{|'
CHARS_PUNCT_END   = '!).?]}>:'
CHARS_PUNCT_QUOTE = '\'"`'
CHARS_PUNCT_LIST  = ';,'
CHARS_PUNCT_OTHER = '#$%&*+-/=@\\^_~'

from enum import Enum

class Meses(Enum):
    JANEIRO = 1
    JAN = 1
    FEVEREIRO = 2
    FEV = 2
    MARCO = 3
    MAR = 3
    ABRIL = 4
    ABR = 4
    MAIO = 5
    MAI = 5
    JUNHO = 6
    JUN = 6
    JULHO = 7
    JUL = 7
    AGOSTO = 8
    AGO = 8
    SETEMBRO = 9
    SET = 9
    OUTUBRO = 10
    OUT = 10
    NOVEMBRO = 11
    NOV = 11
    DEZEMBRO = 12
    DEZ = 12

def obter_ordinal_mes(nome_mes: str) -> int:
    try:
        return Meses[nome_mes.upper()].value
    except KeyError:
        raise ValueError(f"Nome do mês inválido: {nome_mes}")



def requestAsMozilla(url: str):
    """
    Faz uma requisição HTTP para a URL fornecida, imitando o comportamento de um navegador Mozilla.
    Argumentos:
        url (str): A URL para a qual a requisição será feita.
    Retorna:
        requests.Response: O objeto de resposta da requisição.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' # AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    request = Request(url, headers=headers)
    return request


def get_response(url, timeout=30):
    """
    Faz uma requisição HTTP para a URL fornecida e retorna o objeto de resposta.
    """
    try:
        request = requestAsMozilla(url)
        response = urlopen(request, timeout=timeout)
        return response
    except HTTPError as e:
        print(f"Erro ao acessar {url}: {e}")
        return None
    except ConnectionResetError as e:
        print(f"Erro de conexão ao acessar {url}: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

def get_html(url, timeout=30, encoding=None) -> str:
    """
    Faz uma requisição HTTP para a URL fornecida e retorna o conteúdo HTML da resposta.
    """
    response = get_response(url)

    if not response:
        return None

    html = response.read()
    
    # Detectar o encoding se não informado
    if not encoding:
        encoding = detect_encoding(html)

    html = html.decode(encoding=encoding)

    return html, encoding

def save_file(content:bytes|str, filename, encoding=None):
    """
    Salva o arquivo HTML em disco no encoding especificado, se informado.
    """

    path = os.path.dirname(filename)
    file = os.path.basename(filename)

    if not content:
        print('Conteúdo vazio. O arquivo {} não foi salvo em {}.'.format(file, path))
        return 0

    if not os.path.exists(path):
        os.makedirs(path)

    # Detectar o encoding se não informado
    if not encoding:
        # Detectar o encoding do conteúdo HTML
        encoding = detect_encoding(content)
    
    # Se o conteúdo for uma string, converte para bytes
    if isinstance(content, str):
        content = content.encode(encoding=encoding)
    
    with open(os.path.join(path, file), 'wb') as f:
        f.write(content)
        print(f'Arquivo {file} salvo em {path} com encoding {encoding}.')

    return 1


def read_html(path_html, encoding=None) -> str:
    """
    Lê o arquivo HTML do caminho especificado e retorna o conteúdo HTML.
    """

    if encoding:
        # Se o encoding for fornecido, abre o arquivo com o encoding especificado
        with open(path_html, 'r', encoding=encoding) as f:
            html = f.read()
        return html
    else:
        # Se o encoding não for fornecido, detecta o encoding do arquivo
        # Abre o arquivo como bytes para detectar o encoding
        f = open(path_html, 'rb')
        html = f.read()
        f.close()
        
        if html:
            encoding = detect_encoding(html)
            html = html.decode(encoding=encoding)

        return html, encoding

def parse_html(html):
    """
    Faz o parsing do HTML fornecido e retorna o conteúdo textual extraído.
    """
    soup = BeautifulSoup(html, 'html.parser')
    # Remove scripts e estilos
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text()


def extract_legal_text(text):
    """
    Extrai o texto legal do texto fornecido, identificando artigos, parágrafos, incisos, alíneas e itens.
    """
    #soup = BeautifulSoup(html, 'html.parser')
    #text = soup.get_text()
    # matches = regex.finditer(LEGAL_REGEX_PAT, text,
    #                          regex.MULTILINE | regex.DOTALL)
    matches_dispositivos = regex.finditer(DISPOSITIVO_REGEX_PAT, text, regex.MULTILINE)
    matches_metadados    = regex.finditer(METADADOS_REGEX_PAT, text, regex.MULTILINE)
    legal_text = []
    legal_dict = {'art_no':[], 'par_no':[], 'inc_no':[], 'aln_no':[], 'itm_no':[], 'is_cit':[], 'text':[]}
    art_no, par_no, inc_no, aln_no, itm_no, is_cit, text = [], [], [], [], [], [], []
    legislacao_dict = {'apelido':None, 'nome':None, 'tipo':None, 'numero':None, 'ano':None, 'revogada':None, 'conteudo':{}}
    lei_apelido, lei, lei_tipo, lei_num, lei_ano, lei_revogada = None, None, None, None, None, None
    for match in matches_metadados:
        if match.group('lei'):
            legal_text.append(match.group('lei'))

            lei = match.group('lei')
            lei_tipo = match.group('lei_tipo')
            lei_ano = match.group('lei_ano')
            lei_num = match.group('lei_num')
            if lei_num:
                # Remove caracteres especiais
                lei_num = regex.sub(r'[^0-9]', '', lei_num)
            lei_revogada = match.group('revogada')

            if lei_tipo == 'CONSTITUIÇÃO':
                lei_apelido = f"CF/{lei_ano}"
            else:
                lei_apelido = f"{lei_tipo} {lei_num}/{lei_ano}"

            legislacao_dict['apelido'] = lei_apelido
            legislacao_dict['nome'] = lei
            legislacao_dict['tipo'] = lei_tipo
            legislacao_dict['numero'] = lei_num
            legislacao_dict['ano'] = lei_ano
            legislacao_dict['revogada'] = lei_revogada

    for match in matches_dispositivos:
        if match.group('art'):
            legal_text.append(match.group('art'))
            art_no.append(match.group('art_no'))
            par_no.append(None)
            inc_no.append(None)
            aln_no.append(None)
            itm_no.append(None)
            is_cit.append(False)
            text.append(match.group('art_text'))
        elif match.group('par'):
            legal_text.append(match.group('par'))
            art_no.append(art_no[-1])
            par_no.append(match.group('par_no'))
            inc_no.append(None)
            aln_no.append(None)
            itm_no.append(None)
            is_cit.append(False)
            text.append(match.group('par_text'))
        elif match.group('inc'):
            legal_text.append(match.group('inc'))
            art_no.append(art_no[-1])
            par_no.append(par_no[-1])
            inc_no.append(match.group('inc_no'))
            aln_no.append(None)
            itm_no.append(None)
            is_cit.append(False)
            text.append(match.group('inc_text'))
        elif match.group('aln'):
            legal_text.append(match.group('aln'))
            art_no.append(art_no[-1])
            par_no.append(par_no[-1])
            inc_no.append(inc_no[-1])
            aln_no.append(match.group('aln_no'))
            itm_no.append(None)
            is_cit.append(False)
            text.append(match.group('aln_text'))
        elif match.group('itm'):
            legal_text.append(match.group('itm'))
            art_no.append(art_no[-1])
            par_no.append(par_no[-1])
            inc_no.append(inc_no[-1])
            aln_no.append(aln_no[-1])
            itm_no.append(match.group('itm_no'))
            is_cit.append(False)
            text.append(match.group('itm_text'))
        elif match.group('cit'):
            legal_text.append(match.group('cit'))
            art_no.append(art_no[-1])
            par_no.append(par_no[-1])
            inc_no.append(inc_no[-1])
            aln_no.append(aln_no[-1])
            itm_no.append(itm_no[-1])
            is_cit.append(True)
            text.append(match.group('cit'))


    legal_dict['art_no'] += art_no
    legal_dict['par_no'] += par_no
    legal_dict['inc_no'] += inc_no
    legal_dict['aln_no'] += aln_no
    legal_dict['itm_no'] += itm_no
    legal_dict['is_cit'] += is_cit
    legal_dict['text']   += text

    legislacao_dict['conteudo'] = legal_dict

    # Remove linhas vazias
    legal_text = [t.strip() for t in legal_text if t]

    print(f'Encontrados {len(legal_text)} trechos legais.')
    return {'legal_text':'\n'.join(legal_text), 'legislacao_dict':legislacao_dict}


def extrair_data_publicacao(texto):
    """
    Obtém a data de publicação do texto legal, se disponível.
    """

    # Etapa 1: Encontrar todas as linhas de publicacao
    for match_line in regex.finditer(PUBLICACAO_REGEX, texto):
        publicacao_text = match_line.group("publicacao")
        print(f"Linha encontrada: {publicacao_text.strip()}")

        dados = {"publicacao": publicacao_text.strip(), "clbr_data": None, "dou_data": None}

        # Etapa 2: Extrair detalhes da linha encontrada
        match_clbr = regex.search(CLBR_DATA_REGEX, publicacao_text)
        if match_clbr:
            clbr_data = match_clbr.group("clbr_data")
            if clbr_data:
                # Remove caracteres especiais
                data = regex.sub(r'[^0-9]', '', clbr_data)
                dados["clbr_data"] = str(datetime.strptime(data, '%d%m%Y').date())
            print(f"  -> Data CLBR: {dados['clbr_data']}")

        match_dou = regex.search(DOU_DATA_REGEX, publicacao_text)
        if match_dou:
            dou_data = match_dou.group("dou_data")
            if dou_data:
                # Remove caracteres especiais
                data = regex.sub(r'[^0-9]', '', dou_data)
                dados["dou_data"] = str(datetime.strptime(data, '%d%m%Y').date())
            print(f"  -> Data DOU: {dados['dou_data']}")

        return dados
        print("-" * 20)

def extrair_metadados_legislacao(texto):
    """
    Extrai os metadados da legislação do texto fornecido.
    """
    # Regex para capturar os metadados
    metadados = {'lei_tipo':None, 'lei_num':None, 'lei_ano':None, 'lei_data':None, 'lei_revogada':None, 'lei_local':None, 'lei_data_ext':None, 'lei_data_iso':None}
    matches = regex.finditer(METADADOS_REGEX_PAT, texto, regex.MULTILINE)
    for match in matches:
        if match.group('lei'):
            metadados['lei_tipo'] = match.group('lei_tipo')

            metadados['lei_num'] = match.group('lei_num')
            if metadados['lei_num']:
                # Remove caracteres especiais
                metadados['lei_num'] = regex.sub('[^0-9]', '', metadados['lei_num'])
            
            metadados['lei_ano'] = match.group('lei_ano')
            if metadados['lei_ano']:
                # Remove caracteres especiais
                metadados['lei_ano'] = regex.sub('[^0-9]', '', metadados['lei_ano'])

        elif match.group('revogada'):

            metadados['lei_revogada'] = True if match.group('revogada') else False

        elif match.group('local_data'):
            metadados['lei_local'] = match.group('local')
            metadados['lei_data_ext'] = match.group('data')
            
            dia, mes, ano = match.group('local_data_dia'), match.group('local_data_mes'), match.group('local_data_ano')
            metadados['lei_data_iso'] = str(date(int(ano), obter_ordinal_mes(mes), int(dia)))
    
    return metadados


def get_body_from_html(html):
    """
    Faz o parsing do HTML fornecido e retorna o conteúdo textual extraído.
    """
    soup = BeautifulSoup(html, 'html.parser')
    # Remove scripts e estilos
    for script in soup(["script", "style"]):
        script.decompose()
    body = soup.body.get_text()
    return body


def subf(regex_pattern, sub_pattern, text:str|list, flags = regex.MULTILINE | regex.V0):
    
    result = []
    if isinstance(text, list):
        for t in text:
            result.append(regex.subf(regex_pattern, sub_pattern, text, flags=flags))
    else:
        result = regex.subf(regex_pattern, sub_pattern, text, flags=flags)
    
    return result

def sanitize_text(text):
    """
    Limpa o corpo do HTML extraído, removendo caracteres indesejados e formatando corretamente.
    """
    # result = subf(r"(\n \n)", r' ', text)
    # Marca dupla de nova linha com ¢
    result = text
    
    # DOCUMENTAÇÃO: A operação comentada abaixo produz efeitos colaterais no padrão de formatação do texto
    #               esperado para o texto legal. Por isso, foi comentada. Pode ser útil em uma nova versão,
    #               mas requer reavalizar todas as operações de regex que dependem do padrão de formatação
    #               atual.
    # result = '\n'.join([t.strip() for t in result.split('\n')])

    result = subf(r"(\r\n)", ' ', result)
    result = subf(r"(\n *\n)", r'¢', result)
    # Capta concatenações indevidas de linhas e corrige: AbcDef e ABCDef
    result = subf(r"\b(?:([A-Z][a-z]+|[A-Z]+[A-Z])([A-Z][a-z]+))\b", r'{1}¢{2}', result)
    # Capta concatenações indevidas de linhas e corrige: AbcDEF
    result = subf(r"\b(?:([A-Z][a-z]+)([A-Z)][A-Z]+))\b", r'{1}¢{2}', result)
    
    # Insere nova linha onde houver ¢ e concatena
    result = subf(r"¢", '\n', result) # NOVO
    result = '\n'.join(result.split('\n')) # NOVO

    # Marcar com ¢ todas as linhas que começam com um dispositivo legal
    result = subf(DISPOSITIVO_REGEX_PAT, r'¢{0}', result)

    # Marcar com ¢ todas as linhas que começam com o aviso de publicação
    result = subf(PUBLICACAO_REGEX, r'¢{0}', result)

    # Marcar com ¢ todas as linhas que são metadados
    result = subf(METADADOS_REGEX_PAT, r'¢{0}', result, flags=regex.S)

    result = subf(r"( +\n)", ' ', result)

    #result = '¢'.join([t.strip() for t in result.split('\r\n') if t])
    
    # Substitui marcação de recuo por espaço para juntar linhas
    result = ' '.join([t for t in result.split('\r') if t])

    # Remove espaços em branco extras
    result = subf(r" {2,}", ' ', result)
    
    # Insere nova linha onde houver ¢
    result = subf(r"¢", '\n', result)

    # Substitui o caracter unicode \u00A0 (espaço não separável) por espaço
    result = subf(b'\xc2\xa0'.decode('utf-8'), ' ', result)


    # Remove linhas em branco
    result = '\n'.join([l.strip() for l in result.split('\n') if l])

    # Remove tabulações que sobraram
    result = subf(r"(\t)", r'', result)
    print('\nSANITIZED 1\n','-'*80,'\n', result.encode(),'\n', '-'*80)
    return result


def sanitize_legal_text(legal_text):
    """
    Limpa o texto legal extraído, removendo caracteres indesejados e formatando corretamente.
    """

    
    #text1 = subf(r"(\r\n)", r' ', legal_text)
    #result = subf(r"( ){2,}", r' ', result)
    
    # Realiza sanitização básica do texto
    result = sanitize_text(legal_text)

    result = subf(r"\n \w", ' ', result)

    #result = subf(r"(Art)(\s+)(.*)(\s+)", r'Art. {3}', result)
    result = subf(r"(?i)(Art(?:\s*\.*))\s*(\d+(?:o|°|º|[\-A-Z]{1,}))([\s.]*)", r'Art. {2} ', result)
    
    # Identifica artigos quebrados e une as linhas
    result = subf(r"(Art)(.*)([a-zA-z])(\n)", r'{1}{2}{3} ', result)
    # Ajusta espaços entre o final de um texto e um artigo.
    result = subf(r"(.) *\. *(Art)", r'{1}.\n{2}', result)

    # Junta linhas se, respectivamente, a última e a primeira palavras da primeira e segunda linhas são minúsculas.
    #result = subf(r"([a-z])(\n)+([a-z])", r'{1} {3}', result)
    result = subf(r"([a-z])(\n)+([a-z][^).])", r'{1} {3}', result)
    
    #result = subf(r"(\w*|[,]*)(\s*\n)+([a-z]|[,]+|[0-9]+)", r'{1} {3}', result)
    result = subf(r"(\w*|[,]*)(\s*\n)([a-z0-9,]+\s*[a-z]+)", r'{1} {3}', result)
    
    #result = subf(r"(\w)(\s$\n)(\w)", r'{1} {3}', result) # Parece que o regex não aceita ^ nem $
    #result = subf(r"(\w)(\s{1}\n)+(\w)", r'{1} {3}', result)
    result = subf(r"(\w)( +\n)+(\w)", r'{1} {3}', result)
    
    result = subf(r"(\w *)(DECRETO|LEI|CONSTITUI[CÇ][AÃ]O)", r'{1}\n{2}', result)
    # Remove textos ignorados
    result = subf(IGNORE_REGEX, r'', result)

    # Substitui o caracter unicode \u00A0 (espaço não separável) por espaço
    result = subf(b'\xc2\xa0'.decode('utf-8'), ' ', result)
    # Substitui o caracter unicode “ (\u201c; abertura de aspas duplas) por "
    result = subf(b'\xc2\x93'.decode('utf-8'), '"', result)
    # Substitui o caracter unicode ” (\u201d; fechamento de aspas duplas) por "
    result = subf(b'\xc2\x94'.decode('utf-8'), '"', result)

    result = subf(r"(\n){2,}", r'{1}', result)
    result = subf(r" *(,) *\n", r', ', result)
    result = subf(r"(\. *\.)", r'.', result)

    # Corrige vírgulas separadas das palavras por espaço em branco
    result = subf(r"([0-9A-zA-Z]) +, *([0-9A-zA-Z])", r'{1}, {2}', result)
    

    result = '\n'.join([t.rstrip() for t in result.split('\n') if t])

    def parse_line(current, previous):
        
        if not current:
            return False

        if not previous:
            return False
        
        to_join = False
        to_join += current[0] in string.punctuation
        to_join += current[0].isdecimal()
        to_join += current[0].islower()

        found = regex.search(FIRST_WORD_REGEX, current, regex.MULTILINE)
        curr_first_word = found.group() if found else None

        # O primeiro elemento da linha atual é uma palavra
        if curr_first_word:
            if curr_first_word.islower(): # Minúscula
                return True

            if curr_first_word.isdecimal(): # Número (exceto expoentes e )
                return True

        # Pontuação que inicia ou continua um bloco
        if previous[-1] in CHARS_PUNCT_START + CHARS_PUNCT_LIST:
            return True

        if previous[-1] in CHARS_PUNCT_END + CHARS_PUNCT_QUOTE + CHARS_PUNCT_OTHER:
            return False

        found = regex.search(LAST_WORD_REGEX, previous, regex.MULTILINE)
        prev_last_word = found.group() if found else None
        if not prev_last_word:
            return False

        if prev_last_word.islower():
            return True

        return bool(to_join)

    dispositivos_regex = '|'.join(
        [ARTIGO_REGEX, PARAGR_REGEX, INCISO_REGEX, ALINEA_REGEX, ITEM_REGEX])


    # Percorre o texto linha por linha para encontrar parágrafos quebrados
    linhas = result.split('\n')
    result = []
    while linhas:
        prev = result[-1] if len(result) > 0 else None
        curr = linhas[0]
        late = linhas[1] if len(linhas) > 1 else None
        #for i, linha in enumerate(linhas):

        matches_prev = [match for match in regex.finditer(
            dispositivos_regex, prev + '\n', regex.MULTILINE) if match] if prev else None
        
        matches_curr = [match for match in regex.finditer(
            dispositivos_regex, curr + '\n', regex.MULTILINE) if match] if curr else None
        
        matches_late = [match for match in regex.finditer(
            dispositivos_regex, late + '\n', regex.MULTILINE) if match] if late else None

        # Linhas anterior e atual são dispositivos
        if matches_prev and matches_curr:
            join = False
        # Linha anterior é, mas linha atual não é um dispositivo
        elif matches_prev and not matches_curr:
            join = parse_line(curr, prev)
        # Linha anterior não é, mas linha atual é um dispositivo
        elif not matches_prev and matches_curr:
            join = False
        elif not matches_prev and not matches_curr:
            join = parse_line(curr, prev)


        if join:
            result[-1] += ' ' + curr
        else:
            result.append(curr)
        linhas.pop(0)

    result = '\n'.join(result)

    # Corrige e padroniza as datas no texto
    matches = regex.finditer(pattern=DATA_EXTENSO_REGEX, string=result, flags=regex.IGNORECASE|regex.MULTILINE)
    for match in matches:
        data_extenso = match.group('data_extenso')
        if data_extenso:
            dia = match.group('data_ext_dia')
            if dia:
                # Remove caracteres especiais
                dia_new = regex.sub('[^0-9]', '', dia)
            mes = match.group('data_ext_mes')
            ano = match.group('data_ext_ano')
            if ano:
                # Remove caracteres especiais
                ano_new = regex.sub('[^0-9]', '', ano)
            result = regex.subf(data_extenso, f'{dia} de {mes} de {ano_new}', result)

    matches = regex.finditer(pattern=DATA_CURTA_REGEX, string=result, flags=regex.IGNORECASE|regex.MULTILINE)
    for match in matches:
        data_curta = match.group('data_curta')
        if data_curta:
            # Remove caracteres especiais
            data_curta_dia = match.group('data_curta_dia')
            dia = regex.sub('[^0-9]', '', data_curta_dia)

            data_curta_mes = match.group('data_curta_mes')
            mes = regex.sub('[^0-9]', '', data_curta_mes)

            data_curta_ano = match.group('data_curta_ano')
            ano = regex.sub('[^0-9]', '', data_curta_ano)

            data_curta_new = date(int(ano), int(mes), int(dia)).strftime('%d.%m.%Y')
            #data_curta_new = data_curta_new.strftime("%d.%m.%Y")

            result = regex.subf(data_curta, data_curta_new, result)

    return result


def get_body_first_lines(bsObj:BeautifulSoup, max_lines:int=100):
  body = bsObj.body.get_text()
  first_lines = []

  body = sanitize_text(body)
  num_lines = len(body.split('\n'))

  max_lines = num_lines if max_lines > num_lines or max_lines < 1 else max_lines

  print(f'Exibindo {max_lines} linhas de {num_lines}:\n')
  i = max_lines

  for l in body.split('\n'):
    if i == 0:
      break
    linha = l.strip()
    if linha:
      first_lines.append(linha)
      print(f'{max_lines-i+1:<6}: {linha}')
      i -= 1

  return first_lines

def get_legal_text_from_url(url, timeout=30, encoding='utf-8'):
    """
    Obtém o texto legal de uma URL fornecida, fazendo o parsing do HTML e extraindo o conteúdo relevante.
    """
    response = get_response(url, timeout=timeout)

    # bsObj = BeautifulSoup(html, 'html.parser')
    bsObj = BeautifulSoup(response.read().decode(encoding=encoding))
    text = bsObj.body.get_text()

    # Faz limpeza básica do texto (linhas e espaços)
    text = sanitize_text(text)

    # remove espaço antes de nova linha
    # text = subf(r"\n ", '\n', text)
    
    
    # remove espaço criado por caracteres não imprimíveis
    text = subf(b'\xc2\xa0'.decode('utf-8'), '', text)

    return text


def to_pandas(legal_text):
    df_legal = pd.DataFrame(
        columns=['lei_apelido', 'lei_nome', 'lei_tipo', 'lei_numero', 'lei_ano', 'lei_revogada',
                 'artigo', 'parágrafo', 'inciso', 'alínea', 'item', 'citacao', 'texto', ])
    # 'apelido':None, 'nome':None, 'tipo':None, 'numero':None, 'ano':None, 'revogada':None
    if isinstance(legal_text, str):
        # regex para capturar o texto legal
        legal_text_obj = extract_legal_text(legal_text)
    elif isinstance(legal_text, dict):
        legal_text_obj = copy.deepcopy(legal_text)

    print(legal_text_obj)
    
    df_legal['artigo']    = legal_text_obj['legislacao_dict']['conteudo']['art_no']
    df_legal['parágrafo'] = legal_text_obj['legislacao_dict']['conteudo']['par_no']
    df_legal['inciso']    = legal_text_obj['legislacao_dict']['conteudo']['inc_no']
    df_legal['alínea']    = legal_text_obj['legislacao_dict']['conteudo']['aln_no']
    df_legal['item']      = legal_text_obj['legislacao_dict']['conteudo']['itm_no']
    df_legal['citacao']   = legal_text_obj['legislacao_dict']['conteudo']['is_cit']
    df_legal['texto']     = legal_text_obj['legislacao_dict']['conteudo']['text']

    df_legal['lei_apelido']  = legal_text_obj['legislacao_dict']['apelido']
    df_legal['lei_nome']     = legal_text_obj['legislacao_dict']['nome']
    df_legal['lei_tipo']     = legal_text_obj['legislacao_dict']['tipo']
    df_legal['lei_numero']   = legal_text_obj['legislacao_dict']['numero']
    df_legal['lei_ano']      = legal_text_obj['legislacao_dict']['ano']
    df_legal['lei_revogada'] = legal_text_obj['legislacao_dict']['revogada']

    # Remove linhas vazias
    df_legal = df_legal.dropna(how='all')

    return df_legal



def int_to_roman(num):
    """
    Converte um número inteiro (1 a 100) para seu equivalente em algarismo romano.

    A conversão baseia-se na subtração dos maiores valores possíveis primeiro,
    incluindo os casos subtrativos (como IV, IX, XL, XC).

    Argumentos:
        num (int): O número inteiro a ser convertido (deve estar entre 1 e 100).

    Retorna:
        str: A representação do número em algarismo romano.
             Retorna uma mensagem de erro se o número estiver fora do intervalo.
    """
    if not 1 <= num <= 1000:
        return "Número fora do intervalo (1-100)"

    # Mapeamento dos valores e seus símbolos romanos, ordenados do maior para o menor.
    # Inclui os casos subtrativos (90, 40, 9, 4) para simplificar a lógica.
    valores_map = [
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]

    result = ""
    for valor, simbolo in valores_map:
        # Enquanto o número for maior ou igual ao valor atual,
        # adiciona o símbolo romano correspondente e subtrai o valor.
        while num >= valor:
            result += simbolo
            num -= valor

    return result

def int_to_roman_ext(num):
    """
    Converte um número inteiro (1 a 10000) para seu equivalente em algarismo romano,
    utilizando o vinculum (barra superior) para milhares a partir de 4000.

    Argumentos:
        num (int): O número inteiro a ser convertido (deve estar entre 1 e 10000).

    Retorna:
        str: A representação do número em algarismo romano.
             Retorna uma mensagem de erro se o número estiver fora do intervalo.
    """
    if not 1 <= num <= 10000:
        return "Número fora do intervalo (1-10000)"

    # Mapeamento dos valores e seus símbolos romanos, incluindo milhares com vinculum.
    # A barra superior é representada por '\u0305' (Combining Overline).
    # A renderização correta depende da fonte/ambiente.
    # Ordem decrescente é essencial para o algoritmo 'guloso'.
    valores_map = [
        (10000, 'X\u0305'),    # 10000
        (9000, 'IX\u0305'),     # 9000
        (5000, 'V\u0305'),      # 5000
        (4000, 'IV\u0305'),     # 4000
        (1000, 'M'),        # 1000
        (900, 'CM'),        # 900
        (500, 'D'),         # 500
        (400, 'CD'),        # 400
        (100, 'C'),         # 100
        (90, 'XC'),         # 90
        (50, 'L'),          # 50
        (40, 'XL'),         # 40
        (10, 'X'),          # 10
        (9, 'IX'),          # 9
        (5, 'V'),           # 5
        (4, 'IV'),          # 4
        (1, 'I')            # 1
    ]

    result = ""
    # Verifica se o ambiente suporta UTF-8 para o vinculum
    try:
        # Tenta codificar um caractere de teste para verificar o suporte
        'X\u0305'.encode(sys.stdout.encoding or locale.getpreferredencoding())
    except (UnicodeEncodeError, TypeError):
         # Se não suportar, retorna uma mensagem indicando a limitação
         # (ou poderia usar uma representação alternativa como MMMM para 4000, etc.)
         if num >= 4000:
              return f"Num={num}: Representação com vinculum não suportada no ambiente atual."
              # Alternativa (menos padrão): usar M repetido até 3999
              # if num > 3999: return "Número > 3999 (não representável sem vinculum ou MMMM)"

    # Aplica o algoritmo guloso
    for valor, simbolo in valores_map:
        while num >= valor:
            result += simbolo
            num -= valor

    return result
  
def get_files(root_path:str = '.', ext = '*'):

  if not os.path.isdir(root_path):
    print(f"Erro: '{root_path}' não é um diretório válido.")
    return None

  files = []
  for raiz, subpastas, arquivos in os.walk(root_path):

    for _, arquivo in list(product(subpastas, arquivos)):
      if ext == '*' or arquivo.split('.')[-1] == ext:
        files.append(os.path.join(raiz, arquivo))

  files = list(set(files))
  files.sort(reverse=True)
  return files

def sanitize_lines(text:str) -> str:
  text = ' '.join([t.strip() for t in text.split('\n')]).strip()
  return re.sub('(\r\n|\r|\n)', '', text).strip()

def detect_encoding(bytes_sequence:bytes) -> str:
    """
    Detecta o encoding de uma sequência de bytes.
    """

    if isinstance(bytes_sequence, str):
        # Se a entrada for uma string, converte para bytes
        bytes_sequence = bytes_sequence.encode()


    result = chardet.detect(bytes_sequence)
    encoding = result['encoding']
    confidence = result['confidence']
    print(f'Detectado {encoding} com {confidence:.2%} de confiança.')
    return encoding

def obter_metadados_legislacao(html_path, parser = "html.parser", encoding = 'utf-8'):

    with open(html_path, 'r', encoding=encoding) as f:
        html = f.read()

    legislacao = []
    linha = {}
    bsObj = BeautifulSoup(html, parser)
    dataList = bsObj.body.find_all("td", {"class":"visaoQuadrosTd"})
    for data in dataList[2:]:
        if data.a and 'url' not in linha.keys():
            linha["url"] = data.a.get('href')
            linha["numero"] = sanitize_lines(data.a.get_text())
            linha["publicacao"] = sanitize_lines(data.contents[2])

        content = ' '.join([t.strip() for t in data.contents[0].split('\n')])
        content = sanitize_lines(content)
        if content: # and content.lower() not in ['ementa', 'nº do decreto']:
            linha["ementa"] = content

        if 'url' in linha.keys() and 'ementa' in linha.keys():
            legislacao.append(linha)
            linha = {}

    return legislacao