# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 21:08:51 2024

@author: roger
"""
import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import time
import cufflinks as cf
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
from random import random
cf.go_offline()

# [200,128,64,32,3]

print("Hello World")

def copiar_rates(ativo,data_final,num_rates):
    frame = frames[1]# frames[(int(input("Escolha um timeframe: \n0: D1\n1: M15\n2: M1\nResposta:")))]
    rates = mt5.copy_rates_from(ativo, frame, data_final, num_rates)
    return rates
class Trade():
    def __init__(self,spread,moeda,volume,banca):
        self.spread = spread
        self.moeda = moeda
        self.volume = volume
        self.quantidade_de_operacaoes = 0
        self.winrate = 0.5
        self.wins = 0
        self.loses = 0
        self.posicoes_abertas = [] #matriz com dois valores, a primeira posicão é o valor da ordem, a segunda é o tipo 1 compra e -1 venda
        self.banca = banca
        
    def vender(self,valor_real):
        self.posicoes_abertas.append([valor_real-self.spread,-1])
        self.quantidade_de_operacaoes +=1
        # print("Venda feita: %s" % (valor_real-self.spread))
    def comprar(self,valor_real):
        self.posicoes_abertas.append([valor_real+self.spread,1])
        # print("Compra feita: %s" % (valor_real+self.spread))
        self.quantidade_de_operacaoes += 1
    def calcular_banca(self,valor_atual):
        for i in range(len(self.posicoes_abertas)):
            valor_soma = 0
            if self.posicoes_abertas[i][1] == 1:
                # print("Valor atual(C):",valor_atual)
                # print("Posicao(C):",self.posicoes_abertas[i][0])
                # print("valor_soma_banca(C) :",valor_atual - self.posicoes_abertas[i][0])
                self.banca += valor_atual - self.posicoes_abertas[i][0]
                
            else:
                # print("Valor atual(V):",valor_atual)
                # print("Posicao(V):",self.posicoes_abertas[i][0])
                # print("valor_soma_banca(V) :",valor_atual - self.posicoes_abertas[i][0])
                self.banca += self.posicoes_abertas[i][0] - valor_atual

    def fechar_posicao(self,valor_atual):
        for i in range(len(self.posicoes_abertas)):
            valor = 0
            if self.posicoes_abertas[i][1] == 1:
                valor = valor_atual - self.posicoes_abertas[i][0]
                # print("Valor compra: %s" % (valor))
                if valor > 0:
                    self.wins += 1
                if valor < 0:
                    self.loses += 1
            if self.posicoes_abertas[i][1] == (-1):
                valor = self.posicoes_abertas[i][0] - valor_atual
                # print("Valor venda: %s" % (valor))
                if valor > 0:
                    self.wins += 1
                if valor < 0:
                    self.loses += 1
        self.posicoes_abertas = []
        
    def calcular_winrate(self):
        soma = self.wins+self.loses
        if soma > 0:
            self.winrate = self.wins / soma
    
    
class Pesos():
    def __init__(self,linhas,colunas):
        self.linhas = linhas
        self.colunas = colunas
        stddev = np.sqrt(2/linhas)
        self.valores = np.random.randn(linhas, colunas) * stddev
        
class Bias():
    def __init__(self,tamanho):
        self.tamanho = tamanho
        self.valores = np.zeros((tamanho,1))

class RedeNeural():
    def __init__(self,camadas,taxa_dropout,entradas,spread,moeda,volume,banca):
        self.entradas = entradas
        self.camadas = camadas
        self.taxa_dropout = taxa_dropout
        self.bias = []
        self.pesos = []
        self.ultima_saida = [] #neuronio 1 = compra neuronio 2 = venda neuronio 3 = fechar
        self.trade = Trade(spread, moeda, volume, banca)
        
        
        
        for i in range(len(self.camadas)-1):
            self.pesos.append(Pesos(self.camadas[i+1],self.camadas[i]))
            self.bias.append(Bias(self.camadas[i+1]))
    
    def multiplicar_peso(self,entrada,pesos):
        saida_oculta = np.zeros((len(pesos),len(entrada[0])))
        #print(pesos)
        for i in range(len(pesos)):
            
            for j in range(len(entrada[0])):
                soma = 0
                for k in range(len(entrada)):
                    soma += pesos[i][k] * entrada[k][j]
                
                saida_oculta[i][j] = soma
       
        return saida_oculta
    
    def coletar_pesos(self):
        lista_pesos = []
        for w in self.pesos:
            for i in range(w.linhas):
                for j in range(w.colunas):
                    lista_pesos.append(w.valores[i][j])
                    
        return lista_pesos
    def somar_bias(self,oculta_calculada,bias):
        nova_saida = np.zeros((len(oculta_calculada),len(bias[0])))
        for i in range(len(oculta_calculada)):
            nova_saida[i][0] = oculta_calculada[i][0]+bias[i][0]
        return nova_saida

    def ativacao(self,nova_saida):
        return np.maximum(0,nova_saida)
    
    def dropout(self,nova_saida):
        for i in range(len(nova_saida)):
            if random() < self.taxa_dropout:
                nova_saida[i][0] = 0
        return nova_saida
           
                
    def calcular_oculta(self):
        entrada  = self.entradas
        saida = []
        for i in range(len(self.camadas)-1):
            
            saida = self.multiplicar_peso(entrada, self.pesos[i].valores)
            # print("Saida após multiplicar peso\n %s" % (saida),"\n-----------")
            saida = self.somar_bias(saida,self.bias[i].valores)
            # print("Saida após somar bias\n %s" % (saida),"\n-----------")
            saida = self.ativacao(saida)
            # print("Saida após ativação\n %s" % (saida),"\n------------")
            if i+1 != range(len(self.camadas)-1):    
                saida = self.dropout(saida)
            # print("Saida após dropout\n %s" % (saida),"\n---------------")
            entrada = saida
        self.ultima_saida = saida
        return saida
            
    def operar_saida(self,valor_real):
        # print("Valor mercado: ",valor_real)
        if self.ultima_saida[0][0] >0:
          
            self.trade.comprar(valor_real)
        if self.ultima_saida[1][0] >0:
            
            self.trade.vender(valor_real)
        if self.ultima_saida[2][0] > 0:
            
            self.trade.calcular_banca(valor_real)
            self.trade.fechar_posicao(valor_real)
      
        self.trade.calcular_banca(valor_real)
            
            

    

    
if __name__ == "__main__":
    
    mt5.initialize()
    d = mt5.terminal_info()
    d = d._asdict()
    frames = [mt5.TIMEFRAME_D1,mt5.TIMEFRAME_M15,mt5.TIMEFRAME_M1]
    ativo = "USDJPY"
    data_final = time.time()
    quantidade_frames = 10000
    tamanho_entrada = 200
    volume = 0.01
    rates = list(copiar_rates(ativo,data_final,quantidade_frames))
    reverse_rates = rates[::-1]
    grade_de_entradas = []
    lista_de_entradas = []
    for i in range(len(rates)):
        grade_de_entradas.append([rates[i][1]])
        grade_de_entradas.append([rates[i][2]])
        grade_de_entradas.append([rates[i][3]])
        grade_de_entradas.append([rates[i][4]])
        grade_de_entradas.append([rates[i][5]])
    
    primeira_entrada = grade_de_entradas[0:200]
    entradas = primeira_entrada
    camadas = [len(entradas),128,64,32,3]
    taxa_dropout = 0.2
    
    rn = RedeNeural(camadas,taxa_dropout,entradas,0.05,"GPDUSD",0.01,100)
    rn.calcular_oculta()
    rn.operar_saida(primeira_entrada[-2][0])
    
    for i in range(200,quantidade_frames-5,5):
        entradas.pop(0)
        entradas.pop(0)
        entradas.pop(0)
        entradas.pop(0)
        entradas.pop(0)
        entradas.append([grade_de_entradas[i][0]])
        entradas.append([grade_de_entradas[i+1][0]])
        entradas.append([grade_de_entradas[i+2][0]])
        entradas.append([grade_de_entradas[i+3][0]])
        entradas.append([grade_de_entradas[i+4][0]])
        
        rn.entradas = entradas
        rn.calcular_oculta()
        rn.operar_saida(entradas[-2][0])
        # print("Banca: ",rn.trade.banca)
    rn.trade.calcular_winrate()
        
    # plt.hist(pesos_gerais[0].flatten(), bins=50)
    # plt.title("Distribuição dos Pesos Inicializados com LeCun")
    # plt.xlabel("Peso")
    # plt.ylabel("Frequência")
    # plt.show()
