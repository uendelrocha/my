import numpy as np
import pandas as pd
from scipy.stats import skew
from math import ceil

def sturges_rule(df: pd.DataFrame, column_name: str) -> int:
    """
    Calcula o número de faixas (k) pela Regra de Sturges.

    Fórmula: k = 1 + log2(n)
    Onde 'n' é o número de observações.

    Aplicação: Uma regra comum, funciona bem para dados aproximadamente
    normais e com n >= 30. Pode subestimar k para amostras grandes
    ou distribuições não simétricas.
    """
    data = df[column_name].dropna()
    n = len(data)

    if n == 0:
        raise ValueError(f"A coluna '{column_name}' está vazia ou contém apenas NaNs.")
    if data.nunique() == 1: # Todos os valores são iguais
        return 1
    if n == 1: # Apenas uma observação não NaN
        return 1

    k = 1 + np.log2(n)
    return int(ceil(k))

def sqrt_choice_rule(df: pd.DataFrame, column_name: str) -> int:
    """
    Calcula o número de faixas (k) pela Regra da Raiz Quadrada.

    Fórmula: k = sqrt(n)
    Onde 'n' é o número de observações.

    Aplicação: Uma regra muito simples, frequentemente usada como uma
    primeira aproximação ou para datasets menores.
    """
    data = df[column_name].dropna()
    n = len(data)

    if n == 0:
        raise ValueError(f"A coluna '{column_name}' está vazia ou contém apenas NaNs.")
    if data.nunique() == 1:
        return 1
    if n == 1:
        return 1

    k = np.sqrt(n)
    return int(ceil(k))

def scotts_rule(df: pd.DataFrame, column_name: str) -> int:
    """
    Calcula o número de faixas (k) pela Regra de Scott.

    Fórmula: h = (3.49 * s) / (n^(1/3))
             k = (max(dados) - min(dados)) / h
    Onde 's' é o desvio padrão e 'n' é o número de observações.

    Aplicação: Leva em consideração a dispersão dos dados (desvio padrão).
    Mais robusta que Sturges para dados não normais, mas assume que
    os dados são aproximadamente gaussianos para a derivação do fator 3.49.
    Requer n >= 2 para cálculo do desvio padrão.
    """
    data = df[column_name].dropna()
    n = len(data)

    if n == 0:
        raise ValueError(f"A coluna '{column_name}' está vazia ou contém apenas NaNs.")
    if data.nunique() == 1:
        return 1
    if n < 2: # Desvio padrão não é bem definido ou é 0 para n=1
        # print(f"Aviso (Scott's Rule): n < 2 para a coluna '{column_name}'. Retornando 1 faixa.")
        return 1 # Ou poderia chamar sturges_rule para n=1

    s = data.std(ddof=1) # ddof=1 para desvio padrão amostral
    data_range = data.max() - data.min()

    if s == 0: # Se desvio padrão é zero, mas data_range > 0 (improvável se nunique já tratou)
               # Isso implica que todos os dados são iguais, já tratado por nunique()
        return 1

    # Calcula a largura da faixa (h)
    h = (3.49 * s) / (n**(1/3))

    if h == 0:
        # Se h é 0 e data_range > 0, a fórmula resultaria em k infinito.
        # Isso pode ocorrer se 's' for extremamente pequeno mas não zero,
        # ou se n for muito grande tornando o denominador grande.
        # Retornar 'n' significa cada ponto em sua própria faixa, ou usar Sturges.
        # print(f"Aviso (Scott's Rule): Largura da faixa (h) é zero para '{column_name}' com range > 0. Retornando n faixas.")
        return n # Cada ponto em sua própria faixa
    
    k = data_range / h
    return int(ceil(k))


def freedman_diaconis_rule(df: pd.DataFrame, column_name: str) -> int:
    """
    Calcula o número de faixas (k) pela Regra de Freedman-Diaconis.

    Fórmula: h = 2 * IQR / (n^(1/3))
             k = (max(dados) - min(dados)) / h
    Onde 'IQR' é o Intervalo Interquartil (Q3 - Q1) e 'n' é o número de observações.

    Aplicação: Robusta a outliers, pois usa o IQR. Boa para distribuições
    assimétricas. Requer n >= 2 para cálculo do IQR.
    """
    data = df[column_name].dropna()
    n = len(data)

    if n == 0:
        raise ValueError(f"A coluna '{column_name}' está vazia ou contém apenas NaNs.")
    if data.nunique() == 1:
        return 1
    if n < 2: # IQR não é robusto ou pode ser 0 para n=1
        # print(f"Aviso (Freedman-Diaconis): n < 2 para a coluna '{column_name}'. Retornando 1 faixa.")
        return 1 # Ou poderia chamar sturges_rule para n=1

    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1
    data_range = data.max() - data.min()

    if iqr == 0:
        # Se IQR é 0, mas data_range > 0 (ex: [1,1,1,1,10,20]), h será 0.
        # Sturges ou k=n podem ser alternativas mais seguras.
        # Se data_range também for 0, data.nunique() == 1 já teria retornado 1.
        # print(f"Aviso (Freedman-Diaconis): IQR é zero para '{column_name}' com range > 0. Usando Sturges.")
        # Para evitar divisão por zero e fornecer um resultado razoável:
        if data_range > 0:
             return sturges_rule(df, column_name) # Fallback para Sturges
        else: # data_range é 0, então todos os valores são iguais
             return 1


    # Calcula a largura da faixa (h)
    h = (2 * iqr) / (n**(1/3))

    if h == 0: # Pode acontecer se iqr for muito pequeno, mas não zero, e n grande.
        # print(f"Aviso (Freedman-Diaconis): Largura da faixa (h) é zero para '{column_name}' com range > 0. Retornando n faixas.")
        return n # Cada ponto em sua própria faixa

    k = data_range / h
    return int(ceil(k))

def rice_rule(df: pd.DataFrame, column_name: str) -> int:
    """
    Calcula o número de faixas (k) pela Regra de Rice.

    Fórmula: k = 2 * (n^(1/3))
    Onde 'n' é o número de observações.

    Aplicação: Outra regra simples baseada no tamanho da amostra. Tende
    a produzir um número maior de faixas que Sturges para o mesmo n.
    """
    data = df[column_name].dropna()
    n = len(data)

    if n == 0:
        raise ValueError(f"A coluna '{column_name}' está vazia ou contém apenas NaNs.")
    if data.nunique() == 1:
        return 1
    if n == 1:
        return 1

    k = 2 * (n**(1/3))
    return int(ceil(k))

def doanes_rule(df: pd.DataFrame, column_name: str) -> int:
    """
    Calcula o número de faixas (k) pela Regra de Doane.

    Fórmula: k = 1 + log2(n) + log2(1 + |g1| / sigma_g1)
    Onde 'n' é o número de observações, 'g1' é o coeficiente de assimetria,
    e 'sigma_g1' é o desvio padrão do coeficiente de assimetria.
    sigma_g1 = sqrt((6*(n-2)) / ((n+1)*(n+3)))

    Aplicação: Modificação de Sturges para lidar melhor com dados não normais
    (assimétricos). Requer n >= 3 para que sigma_g1 seja bem definido e
    o termo de correção de assimetria seja significativo.
    """
    data = df[column_name].dropna()
    n = len(data)

    if n == 0:
        raise ValueError(f"A coluna '{column_name}' está vazia ou contém apenas NaNs.")
    if data.nunique() == 1:
        return 1

    # Para n < 3, o termo de correção de assimetria não é bem definido ou sigma_g1 é 0.
    # Nesses casos, a regra de Doane frequentemente reverte para Sturges.
    if n < 3:
        # print(f"Aviso (Doane's Rule): n < 3 para a coluna '{column_name}'. Revertendo para Sturges.")
        k_sturges_fallback = 1 + np.log2(n) if n > 0 else 1
        return int(ceil(k_sturges_fallback))

    # Calcula a parte de Sturges
    k_base_sturges = 1 + np.log2(n)

    # Calcula o coeficiente de assimetria (g1)
    # bias=False para o estimador ajustado (não enviesado)
    g1 = skew(data, bias=False)

    # Calcula o desvio padrão do coeficiente de assimetria (sigma_g1)
    # A fórmula é definida para n > 2.
    # Se n=0,1,2, a fórmula pode ter problemas (divisão por zero, raiz de negativo, etc.)
    # O (n-2) no numerador torna sigma_g1=0 para n=2.
    if n <= 2: # Já tratado acima, mas para clareza na lógica de sigma_g1
        sigma_g1 = 0 # Evita erro, mas o termo de correção será problemático se usado.
    else:
        sigma_g1 = np.sqrt((6 * (n - 2)) / ((n + 1) * (n + 3)))

    # Calcula o termo de correção de assimetria
    if sigma_g1 > 0:
        correction_term = np.log2(1 + (np.abs(g1) / sigma_g1))
        k = k_base_sturges + correction_term
    else:
        # Se sigma_g1 é 0 (ex: para n=2) ou negativo (não deveria acontecer com a fórmula),
        # o termo de correção é problemático ou indefinido.
        # Reverter para Sturges é uma abordagem segura.
        k = k_base_sturges
        # print(f"Aviso (Doane's Rule): sigma_g1 <= 0 para '{column_name}'. Usando apenas a parte de Sturges.")

    return int(ceil(k))