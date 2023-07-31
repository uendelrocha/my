import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import skewtest

from IPython.display import display

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
    dfStat.loc['lower'] = dfStat.loc['75%'] - 1.5 * dfStat.loc['iqr']
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
                       first_columns=[], last_columns=[]):

  column_names = list(dataframe.columns.sort_values())
  column_names = [c for c in column_names if c not in first_columns + last_columns]
  
  first_columns.reverse()
  [column_names.insert(0, c) for c in first_columns]
  if len(last_columns) > 0:
    [column_names.append(c) for c in last_columns]
  print(*column_names, sep='\n')
  
  df_result = dataframe[column_names].copy(deep=True) # Cria copia do dataset com colunas ordenadas
  
  return df_result
  

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
