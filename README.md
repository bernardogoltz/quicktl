# Quick TL 

![Logo](assets/logo_ceespufsm.png)

[![PyPI](https://img.shields.io/badge/PyPI-3775A9?logo=pypi&logoColor=fff)](#)
[![GitHub Profile](https://img.shields.io/badge/GitHub-bernardogoltz-181717?style=flat&logo=github)](https://github.com/bernardogoltz) 
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dash.svg?color=dark-green)](https://pypi.org/project/dash/)


https://quicktl-a6zhvyaex8fdzb8zxds5ed.streamlit.app/
## Sobre [... em construção]
 
### A fazer - operação global do sistema
1. ✅ **Escolha do Condutor Ideal** ondições nominais de operação -> Condutor que minimiza custos globais de operação

2. *️⃣ **Cálculo do Parametros** da LT
   
  
   2.1 **Reatancia Indutiva** 
   rmg , dmg . Z = R+jX_l
    
        L = 2*1E-4*ln(DMG/RMG_l) 

        X_L = 75,39822*ln(DMG/RMG_l)  @ 60hz
    2.2 **Reatancia Capacitiva** diametro, distancia media geometrica , altura media em rel. ao solo

    $$C = \frac{2\pi \cdot \varepsilon_0}{\ln\left(\frac{DMG}{RMG_C}\right) - \sigma} $$

     2.3 **Eq. da LT** Gama_l, Z0, ZC ... Finalizar equacionamento e comecar sintese da lt com carga item [3] ; 

3. **Simulacao** // *Input* Carga , Vpu *Output*: Vr, Vs , Ir , Is, VR0 , RT , Xr , Xt , Sr. 




Repositório para otimizar parâmetros de projeto de Linhas de Transmissão. 
