#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 11:03:24 2025

@author: bernardo
"""

import pandas as pd 
import numpy as np 

# Importa funções definidas em conversion.py: robust_convert, excel_pv e generate_series
from conversion import robust_convert, excel_pv, generate_series

# =============================================================================
# FUNÇÕES DE APOIO
# =============================================================================

def load_data(file_path: str) -> pd.DataFrame:
    """
    Carrega o arquivo CSV com os dados dos condutores.

    Parâmetros:
      file_path: caminho do arquivo CSV.
      
    Retorna:
      DataFrame com os dados lidos.
    """
    return pd.read_csv(file_path, encoding='iso-8859-1', delimiter=';')

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomeia colunas e converte as colunas numéricas (exceto "Code word") usando
    a função robust_convert.
    
    Parâmetros:
      df: DataFrame original.
      
    Retorna:
      DataFrame pré-processado.
    """
    df = df.copy()
    df.rename(columns={'20°C (?/km).1': 'R20'}, inplace=True)
    df = df.apply(
        lambda col: col.apply(robust_convert) 
        if col.name != 'Code word' and col.dtype == 'object' else col
    )
    return df

def calculate_parameters(df: pd.DataFrame, T: float, S: float, V: float,
                         FC: float, FP: float, k: float, CME: float,
                         n: int, taxa: float) -> (pd.DataFrame, float):
    """
    Realiza os cálculos dos parâmetros adicionais e gera as colunas de custo.
    
    Parâmetros:
      df: DataFrame pré-processado.
      T, S, V, FC, FP, k, CME, n, taxa: parâmetros do projeto.
      
    Retorna:
      Tuple contendo o DataFrame com os novos cálculos e o valor da corrente.
    """
    corrente = S / (np.sqrt(3) * V)
    
    # Ajuste da resistência com temperatura: R = R20 * (1 + α(T - 20))
    df['R'] = df['R20'] * (1 + df['alpha (1/°C)'] * (T - 20))
    
    # Cálculo das perdas Joule e custo associado
    df['PerdaJoule'] = (corrente ** 2) * df['R']
    df['CustoJoule'] = 8760 * df['PerdaJoule'] * 0.000001 * FP * CME
    
    # Valor presente das perdas para 1 condutor
    df['CustoPerdas'] = (-1) * excel_pv(taxa, n, df['CustoJoule'])
    df['CustoTotal_1'] = df['Preço por km (R$/km)'] + df['CustoPerdas']
    
    # Geração das colunas para as demais opções de condutores (2, 3 e 4)
    for n_cond in [2, 3, 4]:
        col_name = f'CustoTotal_{n_cond}'
        df[col_name] = generate_series(n_cond, df, corrente, FP, CME, taxa, n)
        
    # Define o menor custo e a melhor opção para cada linha
    colunas_custo = ['CustoTotal_1', 'CustoTotal_2', 'CustoTotal_3', 'CustoTotal_4']
    df['CustoTotal_Min'] = df[colunas_custo].min(axis=1)
    df['Melhor_Opção'] = df[colunas_custo].idxmin(axis=1).str.split('_').str[1].astype(int)
    
    return df, corrente

def generate_summary(df: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    """
    Gera os resumos:
      - Por "Code word": custo mínimo e a opção mais frequente.
      - Para cada opção de número de condutores: a linha com o menor custo.
      
    Parâmetros:
      df: DataFrame com os cálculos realizados.
      
    Retorna:
      Tuple com (relatório_por_code, melhores_opcoes_df).
    """
    # Resumo por "Code word"
    relatorio_por_code = df.groupby('Code word').agg(
        Custo_Min=('CustoTotal_Min', 'min'),
        Opção_Barata=('Melhor_Opção', lambda x: x.value_counts().index[0])
    ).reset_index()
    
    # Relatório das melhores opções para cada número de condutores
    lista_opcoes = []
    for n_cond in [1, 2, 3, 4]:
        col_name = f'CustoTotal_{n_cond}'
        min_valor = df[col_name].min()
        melhor_linha = df.loc[df[col_name] == min_valor].iloc[0]
        lista_opcoes.append({
            'n_condutores': n_cond,
            'Custo_Min': min_valor,
            'Code word': melhor_linha['Code word'],
            'Preço por km (R$/km)': melhor_linha['Preço por km (R$/km)']
        })
    melhores_opcoes_df = pd.DataFrame(lista_opcoes)
    return relatorio_por_code, melhores_opcoes_df

def formatar_em_centenas(valor: float) -> str:
    """
    Converte um valor em R$ para unidades de centenas de milhares.
    Por exemplo, 500000 -> "R$ 5.00" (5 x 10^5 R$).
    """
    return f"R$ {valor:,.2f}"

def format_reports(melhores_opcoes_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica a formatação monetária às colunas do relatório.
    """
    df_format = melhores_opcoes_df.copy()
    df_format['Custo_Min_Format'] = df_format['Custo_Min'].apply(formatar_em_centenas)
    df_format['Preço por km (R$/km)_Format'] = df_format['Preço por km (R$/km)'].apply(formatar_em_centenas)
    return df_format

def get_project_parameters_str(T: float, S: float, V: float, FC: float, FP: float,
                               k: float, CME: float, n: int, taxa: float,
                               corrente: float) -> str:
    """
    Gera uma string contendo os parâmetros do projeto.
    """
    parametros = f"""
####################################################
Relatório do Projeto de Otimização de Condutores
####################################################
Parâmetros do Projeto:
------------------------------------
Temperatura (T): {T} °C
Potência (S): {S:.2E} VA
Tensão (V): {V:.2E} V
Fator de Correção (FC): {FC}
Fator de Potência (FP): {FP}
Coeficiente (k): {k}
CME: {CME}
Número de períodos (n): {n}
Taxa de desconto: {taxa}
Corrente (I): {corrente:.2f} A
------------------------------------
"""
    return parametros

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    # Parâmetros do projeto
    T = 100
    S = 1000E6
    V = 500E3
    FC = 0.9
    FP = 0.672
    k = 0.2
    CME = 300
    n = 30
    taxa = 0.08
    file_path = 'data/condutores.csv'
    
    # Carrega e pré-processa os dados
    df = load_data(file_path)
    df = preprocess_data(df)
    
    # Executa os cálculos e gera as colunas de custo
    df, corrente = calculate_parameters(df, T, S, V, FC, FP, k, CME, n, taxa)
    
    # Gera os resumos dos relatórios
    relatorio_por_code, melhores_opcoes_df = generate_summary(df)
    melhores_opcoes_df = format_reports(melhores_opcoes_df)
    
    # Gera a string dos parâmetros do projeto
    parametros_str = get_project_parameters_str(T, S, V, FC, FP, k, CME, n, taxa, corrente)

    
    # Retorna um dicionário com os resultados completos para uso posterior
    return {
         'df_resultado': df,
         'relatorio_por_code': relatorio_por_code,
         'melhores_opcoes_df': melhores_opcoes_df,
         'parametros_str': parametros_str
    }

# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================

if __name__ == '__main__':
    results = main()
    # A variável global "df_resultado" ficará disponível no explorador
    df_resultado = results['df_resultado']
