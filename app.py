# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 14:33:41 2025

@author: Bernardo Ivo Goltz
"""

import streamlit as st
import pandas as pd
from main import load_data, preprocess_data, calculate_parameters

# Remove setas de incremento do number_input
st.markdown('''
<style>
/* Hide HTML5 up/down arrows in number inputs */
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
input[type="number"] {
    -moz-appearance: textfield;
}
</style>
''', unsafe_allow_html=True)

# Título da aplicação e badges
st.title("Otimização de Condutores")
st.markdown(
    "[![GitHub Profile](https://img.shields.io/badge/GitHub-bernardogoltz-181717?style=flat&logo=github)](https://github.com/bernardogoltz)\n"
    "[![LinkedIn](https://img.shields.io/badge/LinkedIn-Bernardo_Ivo_Goltz-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/bernardogoltz)"
    "\n\nBernardo Ivo Goltz \n\n"
    
    "\n\nUFSM - ESP1074 - SISTEMAS DE TRANSMISSÃO DE ENERGIA ELÉTRICA \n\nProfessor Maurício Sperandio\n\n"
    
)

# Sidebar: parâmetros de entrada
st.sidebar.header("Parâmetros do Projeto")

# Temperatura em °C (texto, apenas números)
T_str = st.sidebar.text_input("Temperatura (°C)", "100.0")
try:
    T = float(T_str)
except ValueError:
    st.sidebar.error("Temperatura deve ser um número")
    T = 0.0

# Potência em MVA (texto, apenas números)
S_mva_str = st.sidebar.text_input("Potência (MVA)", "1000.0")
try:
    S_mva = float(S_mva_str)
except ValueError:
    st.sidebar.error("Potência deve ser um número")
    S_mva = 0.0
S = S_mva * 1e6

# Tensão em kV (texto, apenas números)
V_kv_str = st.sidebar.text_input("Tensão (kV)", "500.0")
try:
    V_kv = float(V_kv_str)
except ValueError:
    st.sidebar.error("Tensão deve ser um número")
    V_kv = 0.0
V = V_kv * 1e3

# Outros parâmetros (texto inputs)
FC_str = st.sidebar.text_input("Fator de Correção (FC)", "0.8")
try:
    FC = float(FC_str)
except ValueError:
    st.sidebar.error("FC deve ser um número")
    FC = 0.0

FP_str = st.sidebar.text_input("Fator de Perda (FP)", "0.672")
try:
    FP = float(FP_str)
except ValueError:
    st.sidebar.error("FP deve ser um número")
    FP = 0.0

k_str = st.sidebar.text_input("Coeficiente (k)", "0.2")
try:
    k = float(k_str)
except ValueError:
    st.sidebar.error("k deve ser um número")
    k = 0.0

CME_str = st.sidebar.text_input("Custo Marginal de Energia (CME)", "150.0")
try:
    CME = float(CME_str)
except ValueError:
    st.sidebar.error("CME deve ser um número")
    CME = 0.0

n_str = st.sidebar.text_input("Períodos (n)", "30")
try:
    n = int(n_str)
except ValueError:
    st.sidebar.error("Períodos deve ser um inteiro")
    n = 0

taxa_str = st.sidebar.text_input("Taxa de desconto (decimal)", "0.08")
try:
    taxa = float(taxa_str)
except ValueError:
    st.sidebar.error("Taxa deve ser um número")
    taxa = 0.0

caminho = st.sidebar.text_input("Caminho do CSV", value="data/condutores.csv")

# Botão para executar cálculos
if st.sidebar.button("Calcular"):
    # Carrega e pré-processa os dados
    df_raw = load_data(caminho)
    df     = preprocess_data(df_raw)

    # Calcula parâmetros e custos
    df_calc, corrente = calculate_parameters(df, T, S, V, FC, FP, k, CME, n, taxa)

    # Exibe corrente
    st.write(f"⚡ Corrente: {corrente:.2f} A")

    # Prepara DataFrame de custos
    df_display = df_calc[[
        'Code word',
        'CustoTotal_1',
        'CustoTotal_2',
        'CustoTotal_3',
        'CustoTotal_4'
    ]].copy()
    cols = ['CustoTotal_1','CustoTotal_2','CustoTotal_3','CustoTotal_4']
    df_display[cols] = df_display[cols] / 1e6

    # Estilo: formatação e destaque do mínimo por coluna
    styler = (
        df_display.style
        .format({c: 'R$ {:.2f} M' for c in cols})
        .highlight_min(subset=cols, axis=0, color='lightgreen')
    )
    st.markdown("### Custo Total de Operação por Code Word e Número de Condutores")
    st.dataframe(styler)

    # Calcula custo mínimo e Code word associado para cada configuração
    minimos = []
    for i in [1, 2, 3, 4]:
        c = f'CustoTotal_{i}'
        valor_min = df_calc[c].min()
        code_min  = df_calc.loc[df_calc[c] == valor_min, 'Code word'].iloc[0]
        minimos.append({
            '# de condutores':         i,
            'Code Word':               code_min,
            'Custo Total de Operação': f"R$ {valor_min/1e6:.2f} M"
        })
    df_minimos = pd.DataFrame(minimos)

    # Exibe tabela final
    st.markdown("### Custo Mínimo de Operação por Número de Condutores")
    st.dataframe(df_minimos)

   