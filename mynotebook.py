import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import copy
import myterminal as myt
from scipy.stats import skewtest

from IPython.display import display

from enum import Enum #, unique
from datetime import date, datetime, timedelta

date_format = '%Y-%m-%d' # '2000-01-17'
datetime_format = '%Y-%m-%d %H:%M:%S' # '2000-01-17 13:00:00'

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

def floatCols(dataframe):
    # Get float columns list
    mask = dataframe.dtypes == float
    return dataframe.columns[mask]

def intCols(dataframe):
    # Get int columns list
    return dataframe.select_dtypes('int').columns

def objCols(dataframe):
    # Get int columns list
    return dataframe.select_dtypes('object').columns
  
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
    a_datetime = datetime.strptime(a_datetime, datetime_format)
    
  return datetime(a_datetime) + datetime_part * amount
  
  
  

#%% roundUp & roundDown
def roundUp(number):

  if round(number, 0) > number: # round() rounded up
    result = round(number, 0)
  else: # round() rounded down
    result = round(number, 0) + 1

  return result

def roundDown(number):

  if round(number, 0) < number: # round() rounded up
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

    #print(type(value))
    #print(value)

    if type(value) == pd.Series:
      result = value.apply(lambda x : -np.log1p(abs(x)) if x < 0 else np.log1p(x))
    elif type(value) == np.ndarray:
        # Apply -np.log1p or np.log1p over each value on ndarray
        result = list(map(lambda x : -np.log1p(abs(x)) if x < 0 else np.log1p(abs(x)), [a for a in value]))
    else:
        result = -np.log1p(abs(value)) if value < 0 else np.log1p(value)

    #print(result)

    return result

    '''
    if x < 0:
      return -np.log1p(abs(value))

    return np.log1p(value)
    '''

#%% myDescribe
def myDescribe(dataframe, cols=[]):
    '''
    Customize DataFrame.describe() adding forms and curtosis statistics
    '''

    if len(cols) == 0:
        cols = floatCols(dataframe)

    dfStat = dataframe[cols].describe()

    # Add range
    dfStat.loc['range'] = dfStat.loc['max'] - dfStat.loc['min']

    # Add CV (Coefficient of variation)
    dfStat.loc['cv'] = round(dfStat.loc['std'] / dfStat.loc['mean'], 2)

    # Add QCD (Quartile Coefficient of Dispersion)
    # qcd = (Q3 - Q1) / (Q3 + Q1)
    dfStat.loc['qcd'] = round((dfStat.loc['75%'] - dfStat.loc['25%'])/(dfStat.loc['75%'] + dfStat.loc['25%']), 2)

    # Add iqr
    dfStat.loc['iqr'] = dfStat.loc['75%'] - dfStat.loc['25%']

    # Add lower and upper bounds
    dfStat.loc['lower'] = dfStat.loc['25%'] - 1.5 * dfStat.loc['iqr']
    dfStat.loc['upper'] = dfStat.loc['75%'] + 1.5 * dfStat.loc['iqr']

    # Add Pearson Asimmetry Coefficient
    dfStat.loc['Pearson'] = (3 * (dfStat.loc['mean'] - dfStat.loc['50%'])) / dfStat.loc['std']

    # Add Fisher Skew Coefficient
    '''
    SKEWNESS is a measure of the asymmetry of the probability distribution
    of a real-valued random variable about its mean. The skewness value can be
    positive, zero, negative, or undefined. FOR A UNIMODAL DISTRIBUTION,
    NEGATIVE SKEW COMMONLY INDICATES THAT THE TAIL IS ON THE LEFT SIDE OF THE
    DISTRIBUTION, AND POSITIVE SKEW INDICATES THAT THE TAIL IS ON THE RIGHT.
    In cases where one tail is long but the other tail is fat, skewness does
    not obey a simple rule. For example, a zero value means that the tails on
    both sides of the mean balance out overall; this is the case for a
    symmetric distribution, but can also be true for an asymmetric
    distribution where one tail is long and thin, and the other is short
    but fat.
    '''
    dfStat.loc['Fisher'] = dataframe[cols].skew(axis=0) # scipy.stats.skew(..., bias=False)

    # Add z-score and p-value
    dfStat.loc['z'], dfStat.loc['p'] = skewtest(dataframe[cols], axis=0)

    # Add kurtosis
    dfStat.loc['kurtosis'] = dataframe[cols].kurt(axis=0)


    for col in cols:
      mode = dataframe[col].mode().to_list()

      ## Add Pearson asymmetry
      if 0.00 < abs(dfStat.loc['Pearson', col]) < 0.15:
        dfStat.loc['Pearson asymmetry', col] = 'weak'
      elif 0.15 <= abs(dfStat.loc['Pearson', col]) <= 1.00:
        dfStat.loc['Pearson asymmetry', col] = 'moderate'
      elif abs(dfStat.loc['Pearson', col]) > 1.00:
        dfStat.loc['Pearson asymmetry', col] = 'strong'
      else:
        dfStat.loc['Pearson asymmetry', col] = 'none'

      # Add Fisher asymmetry
      if dfStat.loc['Fisher', col] == 0:
        dfStat.loc['Fisher asymmetry', col] = 'symmetrical'
      elif -0.5 <= dfStat.loc['Fisher', col] <= 0.5:
        dfStat.loc['Fisher asymmetry', col] = 'fairly symmetric'
      elif (-1.0 <= dfStat.loc['Fisher', col] < -0.5) or (0.5 < dfStat.loc['Fisher', col] <= 1):
        dfStat.loc['Fisher asymmetry', col] = 'moderately skewed'
      elif (dfStat.loc['Fisher', col] < -1) or (dfStat.loc['Fisher', col] > 1):
        dfStat.loc['Fisher asymmetry', col] = 'highly skewed'

      # Add skewed
      if dfStat.loc['Fisher', col] == 0:
        dfStat.loc['skewed', col] = 'normal (0)'
      elif dfStat.loc['Fisher', col] < 0:
        dfStat.loc['skewed', col] = 'left (-)'
      elif dfStat.loc['Fisher', col] > 0:
        dfStat.loc['skewed', col] = 'right (+)'

      # Add outlier and distribution aspect
      if dfStat.loc['kurtosis', col] > 3:
        dfStat.loc['outliers', col] = 'high'
        dfStat.loc['aspect', col] = 'leptokurtic'
      elif dfStat.loc['kurtosis', col] < 3:
        dfStat.loc['outliers', col] = 'low'
        dfStat.loc['aspect', col] = 'platykurtic'
      elif dfStat.loc['kurtosis', col] == 3:
        dfStat.loc['outliers', col] = 'normal'
        dfStat.loc['aspect', col] = 'mesokurtic'

      # Add mode
      if len(mode) == len(dataframe):
        dfStat.loc['mode', col] = 'amodal'
      elif len(mode) <= 5:
        dfStat.loc['mode', col] = str(mode)
      else:
        dfStat.loc['mode', col] = 'multimodal'

    # Add count missing values
    dfStat.loc['NaN'] = dataframe[cols].isna().sum().reset_index()[0].to_list()

    # Add Dtypes
    dfStat.loc['Dtype'] = dataframe[cols].dtypes.reset_index()[0].to_list()

    display(dfStat.T)
    #display(df3[float_cols].describe().T)
    dataframe[cols].boxplot(figsize=(15, 5))
    #dataframe[cols].info()

    # df3.boxplot()
    return dfStat.T

#%% delete_overlap_columns
def delete_overlap_columns(df_base, df_assoc, no_delete = []):
  '''
  OBJETIVO
      Remover colunas duplicadas de um dataframe associado a um dataframe base.

  DESCRIÇÃO
      delete_overlap_columns verifica se as colunas em um dataframe base estão
      duplicadas em um dataframe associado. O objetivo deste procedimento é
      evitar o erro overlap columns, que ocorre ao fazer joins entre dataframes
      com colunas repetidas.

  PARÂMETROS
      df_base: dataframe base para comparação. As colunas serão mantidas neste.
      df_assoc: dataframe associado que terá as colunas duplicadas removidas.

  RETORNO
      df_return: uma cópia do dataframe associado sem as colunas duplicadas

  Author (email): UENDEL ROCHA (uendelrocha@gmail.com)
  Last release: 2023/05/03
  '''
  df_return = df_assoc.copy(deep=True)
  for column in df_base.columns:
    if column not in no_delete:
      if column in df_return.columns:
        del df_return[column]

  return df_return

#%% drop_null_columns
def drop_null_columns(dataframe:pd.DataFrame):

  dataframe.dropna(
    axis = 1, # drop columns
    how = 'all', # If all values are NA, drop
    inplace = True
    )

  return dataframe

#%% COLUMNS ORDERBY
def reposition_columns(dataframe:pd.DataFrame,
                       first_columns=[],
                       last_columns=[],
                       no_columns=[]):

  myt.cll()
  print('\rReposicionando colunas. Aguarde...', end=' ')

  column_names = list(dataframe.columns.sort_values())
  column_names = [c for c in column_names if c not in first_columns + last_columns]
  column_names = [c for c in column_names if c not in no_columns]

  # 2023-09-19 Uendel Rocha
  # Realiza uma cópia do parâmetro first_column para conservar seu valor original
  first_columns = copy.deepcopy(first_columns) # Faz uma cópia profunda de first_columns para uma variável local
  first_columns.reverse() # Reverte a ordem da lista (não é sorted(list, reverse=True) nem list.sort(reverse=True))

  [column_names.insert(0, c) for c in first_columns]
  if len(last_columns) > 0:
    [column_names.append(c) for c in last_columns]

  # Lista as colunas reordenadas
  # print(*column_names, sep='\n')

  df_result = dataframe[column_names].copy(deep=True) # Cria copia do dataset com colunas ordenadas

  print(myt.OK('Colunas reposicionadas.'), end=' ')

  return df_result

#%% Converte colunas float para str ou int e remove a parte decimal do valor.
def float_to_floor_cols(dataframe:pd.DataFrame,
                        floor = True, cols = [],
                        astype = 'int64'):
  '''
  float_to_floor_cols

  Autor: Uendel Rocha (uendelrocha@gmail.com)
  Data: 2023-09-22

  Description
  -----------
  Remove a parte decimal de colunas do tipo float em um dataframe. A função
  decide se o tipo da coluna após a truncagem será str ou int. Se a coluna
  tiver algum valor null, a coluna será convertida para str. Se a coluna
  não tiver valor null, a coluna será convertida para int64 ou outro informado
  no parâmetro astype.

  Parameters
  ----------
  dataframe : pd.DataFrame
    O dataframe contendo as colunas do tipo float que serão convertidas.
  floor : bool, optional
    Se True, o valor das colunas serão truncados para remover a parte inteira.
    O valor padrão é True. Se floor for False, o valor da coluna não será
    truncado, mas o tipo será convertido para str.
  cols : list, optional
    Informa a lista de colunas que serão convertidas e/ou truncadas.
    O valor padrão é [] (lista vazia). Se uma lista não for informada, apenas
    as colunas float serão convertidas. Se os valores das colunas não forem
    numéricos (ou não permitirem conversão para inteiro), serão transformados
    em string. Os valores null (None, np.nan) serão convertidos para None.
  astype : str, optional
    Nome do tipo padrão para o qual todas as colunas serão convertidas
    se não houver valor null na coluna. O valor padrão é 'int64'.

  Returns
  -------
  dataframe : pd.DataFrame
    Um cópia do dataframe contendo as colunas convertidas e os valores com
    as partes decimais removidas.

  '''
  
  def floor(value):
    return math.floor(float(value))

  # Reindexa o dataframe
  # dataframe.reset_index(drop=True, inplace=True)

  # Garante que o dataframe passado no parâmetro não seja modificado inplace
  dataframe = dataframe.copy(deep=True)
  none_values = ['NaN', 'nan', 'None', '']

  # Transforma colunas float64 em str, remove decimais
  # Nota: Tipo da coluna é transformado para float quando possui null,
  #       exigindo a utilização do tipo str para remover decimais. Por essa
  #       razão, esta função converte para str em vez de para int.
  if cols is None or cols == []:
    cols = floatCols(dataframe)

  for col in cols:

    myt.cll()
    msg_col = f"\rTruncating {col:<25}" +\
      f"{cols.index(col)+1}/{len(cols):<7}"
    print(msg_col, end=' ')

    dataframe = dataframe.astype({col: str})

    index_nones = []
    # Remove o ponto flutuante das colunas transformadas em string
    if floor:
      try:
        # Tenta primeiro remover de uma vez por coluna
        dataframe[col] = dataframe[col].map(floor, na_action='ignore')
      except:
        # Se não der certo com map, converte cada elemento da coluna
        for i, x in zip(dataframe.index,
                        list(dataframe[col])):
          
          col_text = str(x[0:21].encode('utf8'))
          col_text += '...' if len(col_text) >= 20 else ''
          msg_value = f"{col_text:<23}" +\
            f"{myt.gauge(i+1, dataframe.shape[0],10):>25}"
          myt.cll()
          print(msg_col + msg_value, end='')

          if x is not np.NaN or x is not None:
            try:
              dataframe.loc[i, (col)] = math.floor(float(x))
            except:
              dataframe.loc[i, (col)] = str(dataframe.loc[i, (col)])
              index_nones.append(i)

    if index_nones == []:
      try:
        dataframe = dataframe.astype({col: astype})
      except Exception as E:
        print(f'Ocorreu um erro ao converter {col} para {str(astype)}\t-->', E.args)
        print(f'Aviso: A coluna {col} não foi convertida para {str(astype)}.')
    else:
      # for i_none in index_nones:
      for j in index_nones:
        value = dataframe.loc[j, (col)]
        # Valor do primeiro registro quando há índice duplicado no dataframe
        if type(value) is pd.Series:
          value = value[col].iloc[0]

        if value.strip() in none_values:
            dataframe.loc[j, (col)] = None

  myt.cll()
  print(f"{myt.OK('Dataframe truncated!')}")
  return dataframe


#%% myDistinct
# Return a dataframe with distinct rows
def myDistinct(dataframe, col=''):
    result = pd.DataFrame()

    if isinstance(col, list):
        # Return a DataFrame
        result = dataframe.loc[:, col].drop_duplicates().sort_values(col)
    else:
        # Return a Series
        col = list(dataframe.columns)
        result = dataframe.loc[:, col].drop_duplicates().sort_values(col)

    return result

#%%
# Count and return NaN columns
def myNaN(dataframe):
  return dataframe[dataframe.columns[(dataframe
               .isna().sum() > 1)
             ]
  ].isna().sum().reset_index().rename(
    columns = {
        'index':'Column',
        0:'Count NaN'})
#%% myUpdateCol
# Update one dataframe column
def myUpdateCol (dataframe, col="", old="", new=""):
    dataframe.loc[dataframe[col]==old, [col]]=new

#%% myUpdate
# Update dataframe columns
def myUpdate (dataframe, cols=[], values=[('old', 'new')]):
    result = pd.DataFrame()
    for col in cols:
        for old, new in values:
            myUpdateCol(dataframe, col, old, new)

        # Fazemos um distinct para cada uma das colunas e ordenamos os dados em ordem alfabética
        #distinct.insert(cols.index(col), col, df2.loc[:, col].drop_duplicates().to_numpy())
        #result[col] = df2.loc[:, col].drop_duplicates().sort_values().to_numpy()
        result[col] = myDistinct(dataframe, col).to_numpy()

    # Retorna o resultado da atualização
    return result

#%% myGroupBy
def myGroupBy(dataframe, select_cols=['year', 'gdp', 'state'],
              grouper_cols=['state', 'year'],
              agg_cols=['gdp'], agg_type='sum', agg_having='year >= 2015'):

    grouped = dataframe[select_cols].groupby(grouper_cols)

    if agg_cols:
        grouped = grouped[agg_cols].agg(agg_type).reset_index()
    else:
        if agg_type == 'count':
            grouped = grouped.count()
        elif agg_type == 'sum':
            grouped = grouped.sum()
        elif agg_type == 'max':
            grouped = grouped.max()
        elif agg_type == 'min':
            grouped = grouped.min()
        elif agg_type == 'median':
            grouped = grouped.median()
        elif agg_type == 'mean':
            grouped = grouped.mean()
        else:
            grouped = grouped.count()

    if agg_having:
        grouped = grouped.query(agg_having)

    return grouped

#%% VERIFICAR SE HÁ OBSERVAÇÕES TUPLICADAS EM UM DATAFRAME
def is_duplicated(dataframe, cols:list(), group_by:list()):

  '''
  Objetivo
  --------
  Verificar se há informações tuplicadas em um dataframe.

  Parameters
  ----------
  dataframe : pd.DataFrame()
      Contém o dataset com as observações que se deseja verificar a
      duplicidade.
      Exemplo: dataframe = df_decisoes
  cols : list()
      Uma lista com todas as colunas que serão retornadas e agrupadas.
      Exemplo: cols = ['ID', 'ALEATORIO']
  group_by : list()
      Uma lista com as colunas em cols que sofrerão GROUP BY.
      Exemplo: group_by = ['ID']

  Returns
  -------
  O dataset tuplicado ou vazio.

  '''

  agg_cols = [col for col in cols if col not in group_by]
  if len(agg_cols) > 1:
      having = [c + ' > 1 & ' for c in agg_cols[:-1]]
      having.append(agg_cols[-1] + ' > 1')
      having = ''.join([a for a in having])
  else:
      having = agg_cols[0] + ' > 1'

  #print(f'SELECT count({agg_cols}), {cols} \nGROUP BY {group_by} \nHAVING {having}')

  df = myGroupBy(
    dataframe,
    select_cols=cols,
    grouper_cols=group_by,
    agg_cols=None,
    agg_type='count',
    agg_having=having
    )

  return df.shape[0], df

#%% reset_index
def reset_index(dataframe):
  dataframe = dataframe.reset_index()
  del(dataframe['index'])

  return dataframe

#%% rmOutliers
def rmOutliers(dataframe, cols=[], cumulative=False, verbose=False):
  '''
    Remove outliers and show a report before and after changes
    Se a remoção for cumulativa, o cálculo do iqr é sensível a atualização dos dados e ocorre com os limites atualizados após remoção de outliers
    Se a remoção não for cumulativa, o cálculo do iqr não é sensível a atualização dos dados e oorre com os limites fixados antes da remoção dos outliers
  '''


  result = dataframe.copy()

  if verbose:
    count = result.shape[0]
    total = 0

  for col in cols:


      if verbose:
        print(col)
        before = result.shape[0]
        print('Before:\t', before)

      if cumulative:
        q1, q3 = ( result[col].quantile(0.25), result[col].quantile(0.75) )
        iqr = q3 - q1
      else:
        q1, q3 = ( dataframe[col].quantile(0.25), dataframe[col].quantile(0.75) )
        iqr = q3 - q1

      lower_bound = q1 - 1.5 * iqr
      upper_bound = q3 + 1.5 * iqr

      result = result.loc[~((result[col] < lower_bound) | (result[col] > upper_bound))]

      if verbose:
        after = result.shape[0]
        diff = before - after
        total += diff
        print('After:\t', after)
        print('Diff:\t', diff, f'({round(diff / count * 100, 2)}%)')

  if verbose:
    print('------\nTOTAL:\t', total, f'({round(total / count * 100, 2)}%)', 'outliers removed\n')

  return result

#%% lsOutliers
def lsOutliers(dataframe, cols=[], cumulative=False, verbose=False):

  result = dataframe.copy()
  values = 0
  outliers = 0

  for col in cols:

      if verbose:
        print(col)

        # Get NaN's total
        count = result[col].count() # result.loc[(result[col].isna())].shape[0]
        print('Count:\t\t', '{:8.0f}'.format(count))

      if cumulative:
          q1, q3 = ( result[col].quantile(0.25), result[col].quantile(0.75) )
          iqr = q3 - q1
      else:
          q1, q3 = ( dataframe[col].quantile(0.25), dataframe[col].quantile(0.75) )
          iqr = q3 - q1

      lower_bound = q1 - 1.5 * iqr
      upper_bound = q3 + 1.5 * iqr

      if cumulative:
          temp = result.copy()
          temp = temp.loc[~((temp[col] < lower_bound) | (temp[col] > upper_bound))]
          temp.loc[:, col] = np.nan
          result.loc[temp.index, col] = temp.loc[:, col]
          # Update inliers values to NaN
          # result[col].loc[~((result[col] < lower_bound) | (result[col] > upper_bound))] = np.nan
      else:
          temp = dataframe.copy()
          temp = temp.loc[~((temp[col] < lower_bound) | (temp[col] > upper_bound))]
          temp.loc[:, col] = np.nan
          result.loc[temp.index, col] = temp.loc[:, col]
          #result[col] = temp[col].copy()

      if verbose:
        # Get outliers
        after = result.loc[~(result[col].isna())].shape[0]
        outliers += after
        values += count

        print('Outliers:\t', '{:8.0f}'.format(after), '{:8.2f}%'.format(after / count * 100), '\n')

  if verbose:
    print('TOTAL')
    print('COUNT:\t\t', '{:8.0f}'.format(values), '{:8.2f}%'.format(100))
    print('OUTLIERS:\t', '{:8.0f}'.format(outliers), '{:8.2f}%'.format(outliers / values * 100), '\n')

  return result

#################################################################################################
def get_periods(start_year:int = date.today().year, end_year:int = date.today().year, limit = 5):
  
  if end_year < start_year:
    raise ValueError(f"The value for 'start_year' ({start_year}) "+\
                     f"must be less than or equal to 'end_year' ({end_year}). " +\
                     "It's bigger.")
  
  if limit > 0:
    if end_year - start_year > limit:
      raise ValueError(f"The total range of periods cannot be greater than {limit} years.")
      
    current_year = date.today().year
    if start_year < current_year - limit:
      raise ValueError("The start of the period cannot be earlier than {current_year - limit}.")
    
    if end_year > current_year + limit:
      raise ValueError("The end of the period cannot be later than {current_year + limit}.")
  
  intervals = [ ('01-01', '01-31'),
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

  years = list(range(start_year, end_year + 1))
  periods = []
  for year in years:
    for interval in intervals:
      period = (str(year) + '-' + interval[0], str(year) + '-' + interval[1])
      if interval[1] == '03-01':
        period = (period[0], str(add_date(period[1], DatePart.d, amount = -1)))
      periods.append(period)

  return periods

# =============================================================================
# Informa se um valor é vazio, do tipo None ou um dos tipos np.NaN
# =============================================================================
def in_nones(value):
  NONES = [None, '', np.NaN]
  return value in NONES
    
