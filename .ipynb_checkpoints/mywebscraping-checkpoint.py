import sys
import locale

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
  