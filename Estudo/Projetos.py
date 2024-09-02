# -*- coding: utf-8 -*-
import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import time
import cufflinks as cf
import matplotlib.pyplot as plt
import plotly.graph_objects as go
cf.go_offline()

# ticks são as informações de cada preço
# rates são as informações de close, low, high e open

#mt5.initialize(login=53891739,server="XPMT5-DEMO",password="")

mt5.initialize()
d = mt5.terminal_info()
d = d._asdict()
frames = [mt5.TIMEFRAME_D1,mt5.TIMEFRAME_M15,mt5.TIMEFRAME_M1]
def describe_dict(dicionario):
    for chave in dicionario:
        print(chave, " ===> ",dicionario[chave])
    
def copiar_ticks(ativo,data_inicial,quantidade_ticks):
    flag = mt5.COPY_TICKS_ALL
    dados = mt5.copy_ticks_from(ativo, data_inicial, quantidade_ticks, flag)
    return dados

def copiar_rates(ativo,data_final,num_rates):
    frame = frames[1]# frames[(int(input("Escolha um timeframe: \n0: D1\n1: M15\n2: M1\nResposta:")))]
    rates = mt5.copy_rates_from(ativo, frame, data_final, num_rates)
    return rates

def array_to_table(dados):
    df = pd.DataFrame(dados)
    df['time']
    return df

def coletar_symbols():
    return mt5.symbols_get()

def coletar_info_ativo(ativo):
    return mt5.symbol_info(ativo)

def dict_to_dataframe(dicionario):
    lista = list(dicionario.items())
    
    return pd.DataFrame(lista,columns=['Propriedade','Valor'])
def timestamp_datetime(dataframe,nome_coluna):
    dataframe[nome_coluna] = pd.to_datetime(dataframe[nome_coluna],unit='s')
  
    return dataframe
    
def adicionar_ultimos_valores_csv():
    while True:
       
        closes_ativo = mt5.copy_rates_from_pos(ativo, mt5.TIMEFRAME_M1, 0, quantidade_frames)
        closes_ativo = array_to_table(closes_ativo)
     
        closes_ativo['time'] = pd.to_datetime(closes_ativo['time'],unit='s')
        #ultimo_preço = closes_ativo['close'].iloc[-1]
        pd.DataFrame(closes_ativo.iloc[-1]).T.to_csv('valor_segundo.csv',mode='a',header=False,index=False)
        print(closes_ativo.iloc[-1])  
        time.sleep(2)

def adicionar_ativo_obsm(ativo):
    mt5.symbol_select(ativo,True)


    
ativo = "USDJPY"
data_final = time.time()
quantidade_frames = 50000
volume = 0.01
# rates = copiar_rates(ativo,data_final,quantidade_frames)
# df_rates = array_to_table(rates)
# dt_rates = timestamp_datetime(df_rates, 'time')

rates = copiar_rates(ativo, data_final, quantidade_frames)
ratest = list(copiar_rates(ativo,data_final,quantidade_frames))
rates = pd.DataFrame(rates)
reverse = ratest[::-1]
rates['time'] = pd.to_datetime(rates['time'],unit='s')

fig = go.Figure(data=[go.Candlestick(
    x=rates['time'],
    open=rates['open'],
    high=rates['high'],
    low=rates['low'],
    close=rates['close']
)])


array1 = [2,3,4],[5,6,7],[8,9,10]

dt_array1 = pd.DataFrame(array1)

dt_array1.to_csv('pesos.csv',index=False,header=False)
dt_readed = pd.read_csv('pesos.csv',header=None)
dt_readed.loc[len(dt_readed)] = [11,12,14]


    


fig.update_layout(title='Gráfico de Velas', xaxis_title='Tempo', yaxis_title='Preço')

# Mostrar o gráfico
fig.write_html("grafico_velas.html")
print("Gráfico salvo como grafico_velas.html")

    

rates[['time','open', 'high', 'low', 'close']].iplot(kind='candle', title='Gráfico de Velas')
   

# data_inicial = time.time()
# quantidade_ticks = 10
# dados = copiar_ticks(ativo,data_inicial,quantidade_ticks)

# info_ativo = coletar_info_ativo(ativo)
# dict_info = info_ativo._asdict()
# describe_dict(dict_info)

# print(dicst_to_dataframe(dict_info))


mt5.shutdown()
