#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 11:12:58 2025

@author: bernardo
"""
import numpy as np 
import pandas as pd 

def robust_convert(x):
    """
    Converte uma string que pode representar um número com vírgula ou uma fração para float.
    
    - Se o valor contiver '/', é interpretado como fração e calculado o quociente.
    - Se não, a vírgula é substituída por ponto e a string é convertida para float.
    - Em casos de erro, é retornado np.nan.
    """
    try:
        if isinstance(x, str):
            # Verifica se é uma fração.
            if '/' in x:
                # Dividir a string na barra e remover espaços.
                parts = x.split('/')
                if len(parts) == 2:
                    # Substitui vírgula por ponto em cada parte se necessário.
                    num = float(parts[0].strip().replace(',', '.'))
                    den = float(parts[1].strip().replace(',', '.'))
                    # Retorna a divisão (observando divisão por zero).
                    return num / den if den != 0 else np.nan
                else:
                    # Se houver mais de uma barra, tenta uma conversão padrão.
                    return pd.to_numeric(x.replace(',', '.'), errors='coerce')
            else:
                # Se for apenas número com vírgula, converte normalmente.
                return pd.to_numeric(x.replace(',', '.'), errors='coerce')
        else:
            # Se não for string, tenta converter normalmente
            return pd.to_numeric(x, errors='coerce')
    except Exception as e:
        # Em caso de exceção, retorne np.nan.
        return np.nan
    
    
def excel_pv(taxa, n, pmt, fv=0, tipo=0):
  
    if taxa != 0:
        vp = - (pmt * (1 + taxa * tipo) * (1 - (1 + taxa) ** (-n)) / taxa + fv / ((1 + taxa) ** n))
    else:
        vp = - (pmt * n + fv)
    return vp

def generate_series(n_condutores, df, corrente, FP, CME, taxa, n, fv=0, tipo=0):
    """
    Gera uma Series resultante do cálculo:
    
       custo_n = 8760 * corrente² * df['R'] / n_condutores * 0.000001 * FP * CME
       VP = excel_pv(taxa, n, custo_n, fv, tipo)
       Resultado = (df['Preço por km (R$/km)'] * n_condutores) - VP
    
    Parâmetros:
      n_condutores: int
          Número de condutores.
      df: pd.DataFrame
          DataFrame que deve conter as colunas 'R' e 'Preço por km (R$/km)'.
      corrente: float
          Valor da corrente.
      FP: float
          Fator de potência.
      CME: float
          Fator CME.
      taxa: float
          Taxa de desconto por período (por exemplo, 0.05 para 5%).
      n: int
          Número de períodos.
      fv: float, opcional
          Valor futuro residual (default = 0).
      tipo: int, opcional
          Tipo de pagamento (0 = fim do período, 1 = início do período).
          
    Retorna:
      pd.Series: Resultado do cálculo para cada linha do DataFrame.
    """
    # Cálculo de custo_n em cada linha (operações vetorizadas)
    custo_n = 8760 * (corrente ** 2) * df['R'] / n_condutores * 0.000001 * FP * CME
    
    # Calcula o valor presente (VP) para cada linha utilizando a função excel_pv
    vp = excel_pv(taxa, n, custo_n, fv, tipo)
    
    # Cálculo do resultado final: (Preço por km * n_condutores) - VP
    resultado = (df['Preço por km (R$/km)'] * n_condutores) - vp
    
    return resultado