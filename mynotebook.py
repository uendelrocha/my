import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging


from enum import Enum #, unique
from datetime import date, datetime, timedelta

import mylogger

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

'''
NOTA IMPORTANTE
    - Para que o logging funcione corretamente, é necessário chamar 
    mylogger.setup_logging('nome_app') no início do script principal antes de 
    importar este módulo.
'''

DATE_FORMAT = '%Y-%m-%d' # '2000-01-17'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S' # '2000-01-17 13:00:00'

CURRENT_DATE = datetime.now().strftime(DATE_FORMAT)
YESTERDAY_DATE = (datetime.now() - timedelta(days=1)).strftime(DATE_FORMAT)

class DatePart():
    y   = timedelta(days    = 365)
    M   = timedelta(days    =  30)
    w   = timedelta(weeks   =   1)
    d   = timedelta(days    =   1)

class DateTimePart(DatePart):
    h   = timedelta(hours        = 1)
    m   = timedelta(minutes      = 1)
    s   = timedelta(seconds      = 1)
    ms  = timedelta(milliseconds = 1)
    mus = timedelta(microseconds = 1)

def add_date(a_date:date = date.today(), date_part:DatePart=DatePart.d, amount:int = 0):
    '''
    Adiciona uma quantidade de tempo a uma data informada no formato 'Y-M-D'.

    Parameters
    ----------
    a_date : date, optional
        DESCRIPTION. Uma data qualquer no formato 'Y-M-D'. Exemplo: '2000-01-17'.
        O valor default é date.today(). O tipo pode ser str ou datetime.date.
        Sendo str, o valor será convertido para datetime.date.
    date_part : DatePart, optional
        DESCRIPTION. A proporção de tempo na qual será aplicado valor em amount.
        O valor default é DatePart.d, indicando que amount será multiplicado
        pela proporção de 1 dia. Se for informado DatePart.y, amount será
        multiplicado por 365.
        
    amount : int, optional
        DESCRIPTION. A quantidade de tempo que será aplicada à data informada.
        O valor em amount pode ser positivo (indicando futuro em relação à data
        informada) ou negativo (indicando passado). Se o amount for 0, a função
        retornará a data informada no formato datetime.date.
        O valor padrão é 0.

    Returns
    -------
    TYPE
        DESCRIPTION. Retorna a soma ou subtração da
        quantidade de tempo proporcional (dias, anos, meses) apl

    '''
    if type(a_date) is str:
        a_date = tuple(int(d) for d in a_date.split('-'))
        a_date = date(*a_date)
    
    return a_date + date_part * amount
    
def add_datetime(a_datetime:datetime = datetime.now(), datetime_part:DateTimePart=DateTimePart.s, amount:int = 0):
    
    if type(a_datetime) is str:
        a_datetime = datetime.strptime(a_datetime, DATETIME_FORMAT)
        
    return datetime(a_datetime) + datetime_part * amount
    
#%% roundUp & roundDown
def roundUp(number):

    if round(number, 0) >= number: # round() rounded up
        result = round(number, 0)
    else: # round() rounded down
        result = round(number, 0) + 1

    return result

def roundDown(number):
    if round(number, 0) <= number: # round() rounded up
        result = round(number, 0)
    else: # round() rounded down
        result = round(number, 0) - 1

    return result
    #(round(cities_succ, 0) + 1) if (cities_succ - round(cities_succ, 0)) > 0 else cities_succ

#%% myLog1p
def myLog1p(value):
    '''
    Function: myLog1p(value)
    Objective: return numpy.log1p
    Parameter: value must be a pandas.Series, a numpy.ndarray or a scalar

    Calcula o log(1+x) de cada valor numa série ou array, ou o log(1+x) de um escalar
    '''

    #logger.debug(f"type(value): {type(value)}")
    #logger.debug(f"value: {value}")

    if type(value) == pd.Series:
        result = value.apply(lambda x : -np.log1p(abs(x)) if x < 0 else np.log1p(x))
    elif type(value) == np.ndarray:
        # Apply -np.log1p or np.log1p over each value on ndarray
        result = list(map(lambda x : -np.log1p(abs(x)) if x < 0 else np.log1p(abs(x)), [a for a in value]))
    else:
        result = -np.log1p(abs(value)) if value < 0 else np.log1p(value)

    #logger.debug(f"result: {result}")

    return result

    '''
    if x < 0:
        return -np.log1p(abs(value))

    return np.log1p(value)
    '''

def get_months(year:int):
    intervals = [ 
        ('01-01', '01-31'),
        ('02-01', '03-01'), # O mês de fevereiro é calculado
        ('03-01', '03-31'),
        ('04-01', '04-30'),
        ('05-01', '05-31'),
        ('06-01', '06-30'),
        ('07-01', '07-31'),
        ('08-01', '08-31'),
        ('09-01', '09-30'),
        ('10-01', '10-31'),
        ('11-01', '11-30'),
        ('12-01', '12-31') ]
    
    months = []
    for interval in intervals:
        month = (str(year) + '-' + interval[0], str(year) + '-' + interval[1])
        if interval[1] == '03-01':
            month = (month[0], str(add_date(month[1], DatePart.d, amount = -1)))
        months.append(month)
        
    return months

def get_month(year, month:int):
    if 1 <= month <= 12:
        return get_months(year)[month - 1]

# Extrai o ano de uma data informada no formato especificado
def extract_year(a_date: str, date_format: str = DATE_FORMAT) -> int:
    return datetime.strptime(a_date, date_format).year

# Extrai o mês de uma data informada no formato especificado
def extract_month(a_date: str, date_format: str = DATE_FORMAT) -> int:
    return datetime.strptime(a_date, date_format).month

# Extrai o dia de uma data informada no formato especificado
def extract_day(a_date: str, date_format: str = DATE_FORMAT) -> int:
    return datetime.strptime(a_date, date_format).day
     

def get_periods(start_year:int = date.today().year, end_year:int = date.today().year, limit = 10, allow_future:bool = True):
    
    if end_year < start_year:
        raise ValueError(f"The value for 'start_year' ({start_year}) "+\
                         f"must be less than or equal to 'end_year' ({end_year}). " +
                         "It's bigger.")
    
    current_year = date.today().year

    if start_year > current_year and not allow_future:
        raise ValueError(f"The value for 'start_year' ({start_year}) " +
                         f"must be less than or equal to the current year ({current_year}), " +
                         "or allow_future must be True. " +
                         "It's bigger and start in the future is not allowed.")

    if end_year > current_year and not allow_future:
        end_year = current_year

    if limit > 0:
        year_range = end_year - start_year
        if year_range > limit:
            raise ValueError(
                f"The year range ({year_range} years) exceeds the limit of {limit} years. "
                f"To process a larger range, adjust the 'limit' parameter in the function call."
            )
        
        if start_year < current_year - limit:
            raise ValueError("The start of the period cannot be earlier than {current_year - limit} years.")
        
        if end_year > current_year + limit:
            raise ValueError("The end of the period cannot be later than {current_year + limit} years.")
    

    years = list(range(start_year, end_year + 1))
    periods = []
    for year in years:
        periods += get_months(year)

    return periods

def current_date(date_format: str = DATE_FORMAT):
    return datetime.now().strftime(date_format)

def yesterday_date(date_format: str = DATE_FORMAT):
    return (datetime.now() - timedelta(days=1)).strftime(date_format)

def current_year():
    return date.today().year

def is_past_date(a_date: str, date_format: str = DATE_FORMAT):
    curr_date = datetime.strptime(current_date(date_format), date_format)
    if isinstance(a_date, str):
        return datetime.strptime(a_date, date_format) < curr_date
    elif isinstance(a_date, datetime):
        return a_date < curr_date
    elif isinstance(a_date, date):
        return a_date < date.today()

def is_current_date(a_date: str, date_format: str = DATE_FORMAT):
    curr_date = datetime.strptime(current_date(date_format), date_format)
    if isinstance(a_date, str):
        return datetime.strptime(a_date, date_format) == curr_date
    elif isinstance(a_date, datetime):
        return a_date == curr_date
    elif isinstance(a_date, date):
        return a_date == date.today()

def is_future_date(a_date:str, date_format:str = DATE_FORMAT):
    curr_date = datetime.strptime(current_date(date_format), date_format)
    if isinstance(a_date, str):
        return datetime.strptime(a_date, date_format) > curr_date
    elif isinstance(a_date, datetime):
        return a_date > curr_date
    elif isinstance(a_date, date):
        return a_date > date.today()

def is_valid_date(a_date: str, date_format: str = DATE_FORMAT):
    try:
        if isinstance(a_date, str):
            datetime.strptime(a_date, date_format)
        elif isinstance(a_date, date):
            a_date.strftime(date_format)
        return True
    except:
        return False

def is_valid_date_format(date_format: str):
    try:
        date.today().strftime(date_format)
        return True
    except:
        return False

def get_dates(start_date:str, end_date:str, sep:str = '-', 
              date_format:str = DATE_FORMAT, reverse = False) -> list:

    result = []

    if not is_valid_date_format(date_format):
        raise ValueError(
            f"Invalid date format '{date_format}'. ")

    # Check if both dates are valid
    if isinstance(start_date, str) and not is_valid_date(start_date, date_format):
        raise ValueError(f"Invalid start date '{start_date}'. ")
    if isinstance(end_date, str) and not is_valid_date(end_date, date_format):
        raise ValueError(f"Invalid end date '{end_date}'. ")

    # Check if both dates are dates
    if isinstance(start_date, date) and isinstance(end_date, date):
        start_period = start_date
        end_period = end_date
    elif sep == '':
        # If the separator is empty, the date format will be used as separator
        start_period = datetime.strptime(start_date, date_format)
        end_period = datetime.strptime(end_date, date_format)
    elif sep not in start_date or sep not in end_date:
        raise ValueError(f"Invalid separator '{sep}' in start_date or end_date. " +
                         "The separator must be present in both dates.")
    else:
        start_year, start_month, start_day = [int(x) for x in start_date.split(sep)]
        start_period = date(start_year, start_month, start_day)

        end_year, end_month, end_day = [int(x) for x in end_date.split(sep)]
        end_period = date(end_year, end_month, end_day)

    # If the start date is greater than the end date, the dates are swapped
    if start_period > end_period:
        start_period, end_period = end_period, start_period

    curr_date = start_period
    while curr_date <= end_period:
        result.append(curr_date.strftime(date_format))
        curr_date = add_date(curr_date, DatePart.d, amount = 1)
    
    result.sort(reverse=reverse)
        
    return result

def get_interval(start:str = YESTERDAY_DATE, end:str = CURRENT_DATE, 
                 extract_dates:bool = True, 
                 sep:str = '-', 
                 date_format:str = DATE_FORMAT,
                 reverse = False,
                 limit = 0,
                 allow_future:bool = True,
):
    """Gera intervalos de datas.

    Esta função gera intervalos de datas, retornando tuplas 
    contendo pares de datas ou períodos, dependendo dos parâmetros.

    Args:
        start: Data de início do intervalo (padrão: '1988-09-22').
        end: Data de fim do intervalo (padrão: '1988-10-05').
        get_dates: Se True, retorna datas individuais dentro do intervalo. 
                   Se False, retorna tuplas com as datas de início e fim de 
                   cada período (padrão: True).
        sep: Separador usado na formatação da data (padrão: '-').
        date_format: Formato da data (padrão: myn.date_format).
        reverse: Se True, as datas são geradas em ordem decrescente 
                 (padrão: True).
        allow_future: Se True, permite datas futuras. Se False, ignora 
                      datas futuras (padrão: False).

    Yields:
        Tuplas contendo pares de datas ou períodos, dependendo do 
        parâmetro `get_dates`.

    Examples:
        >>> for data, _ in get_interval():
        ...   logger.info(data)
        1988-09-22
        1988-09-23
        ...
        1988-10-05

        >>> for periodo in get_interval(get_dates=False):
        ...   logger.info(periodo)
        ('1988-09-22', '1988-10-05')

    """
    try:
        start = int(start)
        end   = int(end)

        periods = get_periods(start, end, limit, allow_future)
        periods = sorted(periods, reverse=reverse)
    except:
        if is_future_date(start) and not allow_future:
            raise ValueError(f"Data de início {start} é futura.")

        if is_future_date(end) and not allow_future:
            end = str(date.today().strftime(date_format))

        periods = [(start, end)]

    for period in periods:
        if not is_future_date(period[0]) or allow_future:
            if extract_dates:
                dates = get_dates(period[0], period[1], 
                                      sep=sep, date_format=date_format, 
                                      reverse=reverse)
                for date in dates:
                    yield (date, date)
            else:
                yield period


# =============================================================================
# Informa se um valor é vazio, do tipo None ou um dos tipos np.nan
# =============================================================================
# String vazia não é None.
NONES = [None, pd.NaT, np.nan, 'NaT', 'nan', 'NaN', 'None', '<NA>']

def in_nones(value):
    return value in NONES

def calc_object_size(obj):
    """
    Calcula o tamanho em bytes de um objeto complexo, incluindo seus elementos internos.
    """
    seen = set()
    def sizeof(o):
        if id(o) in seen:
            return 0
        seen.add(id(o))
        size = sys.getsizeof(o)
        if isinstance(o, dict):
            size += sum(sizeof(k) + sizeof(v) for k, v in o.items())
        elif isinstance(o, (list, tuple, set, frozenset)):
            size += sum(sizeof(i) for i in o)
        return size
    return sizeof(obj)
    

def human_bytes(size):
    """
    Converte um tamanho em bytes para um valor legível em KB, MB, GB, etc.
    """
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.2f} {unit}"

def human_seconds(seconds):
    """
    Converte segundos em ano, mês, semanas, dias, horas, minutos, segundos.
    Retorna no formato 0h00min0.000s
    """
    seconds = float(seconds)
    times = {'h': 0, 'min': 0, 's':0}
    for unit in times.keys():
        match unit:
            case 'h':
                divisor = 60 * 60
            case 'min':
                divisor = 60
            case 's':
                divisor = 1

        times[unit] = int(seconds // divisor)
        seconds = seconds % divisor

        if seconds < 60.0:
            times['s'] = seconds
            break

    return f"{times['h']:9}h{times['min']:02}min{times['s']:.3f}s"