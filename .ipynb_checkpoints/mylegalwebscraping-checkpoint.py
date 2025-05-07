import sys
import locale
import pandas as pd

from urllib import response
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from bs4 import BeautifulSoup

import regex # pip install regex

LEGAL_REGEX_PAT = r'(?P<art>^(Art. \d*\W*)(?P<art_text>.*)(\n))|(?P<cit>^(\")(\w*|\W)*(\")$)|(?P<par>^(§ \d*\W\s*|Par[áa]grafo [ÚúUu]nico\W\s*)(?P<par_text>.*)(\n))|(?P<inc>^([IVXLCDM]{1,3}[IVXLCDM]{0,3}[IVXLCDM]{0,3}[IVXLCDM]{0,3})(\s+-{0,1}\s{0,1})(?P<inc_text>.+)(\n))|(?P<aln>^([a-z]+\)\s*)(?P<aln_text>.*)(\n))|(?P<itm>^([1-9]+\W\s*)(?P<itm_text>.*)(\n))'


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


def get_html(url, timeout=30):
    """
    Faz uma requisição HTTP para a URL fornecida e retorna o conteúdo HTML da resposta.
    """
    try:
        request = requestAsMozilla(url)
        response = urlopen(request, timeout=timeout)
        html = response.read()
        return html
    except HTTPError as e:
        print(f"Erro ao acessar {url}: {e}")
        return None
    except ConnectionResetError as e:
        print(f"Erro de conexão ao acessar {url}: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None


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
    matches = regex.finditer(LEGAL_REGEX_PAT, text,
                             regex.MULTILINE | regex.DOTALL)
    legal_text = []
    for match in matches:
        if match.group('art'):
            legal_text.append(match.group('art'))
        elif match.group('par'):
            legal_text.append(match.group('par'))
        elif match.group('inc'):
            legal_text.append(match.group('inc'))
        elif match.group('aln'):
            legal_text.append(match.group('aln'))
        elif match.group('itm'):
            legal_text.append(match.group('itm'))
        elif match.group('cit'):
            legal_text.append(match.group('cit'))

    return '\n'.join(legal_text)


def sanitize_legal_text(legal_text):
    """
    Limpa o texto legal extraído, removendo caracteres indesejados e formatando corretamente.
    """
    # Remove espaços em branco extras e formata o texto
    legal_text = regex.sub(r'\s+', ' ', legal_text)
    legal_text = regex.sub(r'^\s+|\s+$', '', legal_text)
    return legal_text


def get_legal_text_from_url(url, timeout=30):
    """
    Obtém o texto legal de uma URL fornecida, fazendo o parsing do HTML e extraindo o conteúdo relevante.
    """
    try:
        resquest = requestAsMozilla(url)
        response = urlopen(resquest, timeout=timeout)
    except HTTPError as e:
        print(f'Erro HTTP ao acessar {url}: "{e}"')
        return None
    except ConnectionResetError as e:
        print(f'Conexão foi reiniciada ao acessar {url} com o erro: "{e}"')
        return None

    # bsObj = BeautifulSoup(html, 'html.parser')
    bsObj = BeautifulSoup(response.read().decode(encoding='latin-1'))
    text = bsObj.body.get_text()

    # \N{CARRIAGE RETURN} + \N{LINE FEED}
    text = regex.subf(r"(\r\n)", r' ', text)
    # substitui 2 ou mais espaços por 1 espaço
    text = regex.subf(r"( ){2,}", r' ', text)
    # remove tab
    text = regex.subf(r"(\t)", r'', text)
    # remove espaço antes de nova linha
    text = regex.subf(r"\n ", '\n', text)
    # remove espaço depois de nova linha
    text = regex.subf(b'\xc2\xa0'.decode('utf-8'), '', text)

    return text


def to_pandas(legal_text):
    df_legal = pd.DataFrame(
        columns=['lei', 'artigo', 'parágrafo', 'inciso', 'alínea', 'item', 'texto'])

    # regex para capturar o texto legal
    legal_text_cleaned = extract_legal_text(legal_text).split('\n')

    for line in legal_text_cleaned:
        # regex para capturar o texto legal
        match = regex.match(LEGAL_REGEX_PAT, line)
        if match:
            art = match.group('art')
            par = match.group('par')
            inc = match.group('inc')
            aln = match.group('aln')
            itm = match.group('itm')
            text = match.group('art_text') | match.group('par_text') | match.group('inc_text') | match.group('aln_text') | match.group('itm_text')
            # Adiciona os dados ao DataFrame
            df_legal = df_legal.append({
                'lei': 'Lei',
                'artigo': art,
                'parágrafo': par,
                'inciso': inc,
                'alínea': aln,
                'item': itm,
                'texto': text
            }, ignore_index=True)

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
  