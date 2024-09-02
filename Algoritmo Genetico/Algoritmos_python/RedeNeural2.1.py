# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 21:08:51 2024

@author: roger
"""
import MetaTrader5 as mt5
import time
import matplotlib.pyplot as plt
import numpy as np
import json
import pandas as pd
from datetime import datetime

def copiar_rates(ativo, num_rates, frame):
    rates = mt5.copy_rates_from_pos(ativo, frame, 0, num_rates)
    return rates

def criar_grade(rates):
    grade_de_entradas = []
    for rate in rates:
        grade_de_entradas += [[rate['open']], [rate['high']], [rate['low']], [rate['close']], [rate['tick_volume']]]
    return grade_de_entradas


class Trade:
    def __init__(self, spread, moeda, volume, banca):
        self.spread = spread
        self.moeda = moeda
        self.volume = volume
        self.quantidade_de_operacoes = 0
        self.winrate = 0.5
        self.wins = 0
        self.loses = 0
        self.posicoes_abertas = []
        self.banca = banca
        self.historico_banca = []
        
        
    def vender(self, valor_real):
        self.posicoes_abertas.append([valor_real - self.spread, -1])
        self.quantidade_de_operacoes += 1

    def comprar(self, valor_real):
        self.posicoes_abertas.append([valor_real + self.spread, 1])
        self.quantidade_de_operacoes += 1

    def calcular_banca(self, valor_atual):
        for posicao in self.posicoes_abertas:
            if posicao[1] == 1:
                self.banca += valor_atual - posicao[0]
                print(valor_atual)
            else:
                self.banca += posicao[0] - valor_atual
                print(valor_atual)

    def fechar_posicao(self, valor_atual):
        for posicao in self.posicoes_abertas:
            valor = valor_atual - posicao[0] if posicao[1] == 1 else posicao[0] - valor_atual
            if valor > 0:
                self.wins += 1
            else:
                self.loses += 1
        self.posicoes_abertas = []

    def calcular_winrate(self):
        soma = self.wins + self.loses
        if soma > 0:
            self.winrate = self.wins / soma

class Pesos:
    def __init__(self, linhas, colunas):
        self.valores = np.random.randn(linhas, colunas) * np.sqrt(2/linhas)

class Bias:
    def __init__(self, tamanho):
        self.valores = np.zeros((tamanho, 1))

class RedeNeural:
    def __init__(self, camadas, taxa_dropout, entradas, spread, moeda, volume, banca):
        self.entradas = np.array(entradas).reshape(-1, 1)
        self.camadas = camadas
        self.taxa_dropout = taxa_dropout
        self.bias = [Bias(camada) for camada in camadas[1:]]
        self.pesos = [Pesos(camadas[i+1], camadas[i]) for i in range(len(camadas)-1)]
        self.trade = Trade(spread, moeda, volume, banca)
        self.ultima_saida = []
        
    def salvar_pesos_bias(self, filename):
        data = {
            'pesos': [p.valores.tolist() for p in self.pesos],
            'bias': [b.valores.tolist() for b in self.bias]
        }
        with open(filename, 'w') as f:
            json.dump(data, f)

    def carregar_pesos_bias(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        for i, p in enumerate(data['pesos']):
            self.pesos[i].valores = np.array(p)
        for i, b in enumerate(data['bias']):
            self.bias[i].valores = np.array(b)

    def calcular_oculta(self):
        entrada = self.entradas
        for i in range(len(self.camadas) - 1):
            saida = np.dot(self.pesos[i].valores, entrada) + self.bias[i].valores
            saida = np.maximum(0, saida)  # ReLU
            if i < len(self.camadas) - 2:
                saida *= (np.random.rand(*saida.shape) > self.taxa_dropout)
            entrada = saida
        self.ultima_saida = entrada
        return entrada

    def operar_saida(self, valor_real):
        if self.ultima_saida[0, 0] > 0:
            self.trade.comprar(valor_real)
        if self.ultima_saida[1, 0] > 0:
            self.trade.vender(valor_real)
        if self.ultima_saida[2, 0] > 0:
            self.trade.calcular_banca(valor_real)
            self.trade.fechar_posicao(valor_real)
        self.trade.calcular_banca(valor_real)

    def rede_start(self,quantidade_frames,entradas,grade_de_entradas):
        for i in range(0, quantidade_frames):
            if i == 0:
                self.entradas = np.array(entradas).reshape(-1, 1)
            else:
                entradas = entradas[5:] + grade_de_entradas[i*5:(i*5)+5]
                self.entradas = np.array(entradas).reshape(-1, 1)
            
            # Verificação no loop principal
            # if i % 99 == 0:  # Verifica a cada 100 iterações
                # print(f"Iteração {i}, timestamp do último dado: {timestamp_to_date(rates[i]['time'])}")

            self.calcular_oculta()
            # print(entradas[-2][0])
            self.operar_saida(entradas[-2][0])
            self.trade.historico_banca.append(rn.trade.banca)
            if self.trade.banca <0:
                break
    def imprimir_infos_rede(self):
        print("Winrate:", self.trade.winrate)
        print("Banca final:", self.trade.banca)
        print("Quantidade de operações: ", self.trade.quantidade_de_operacoes)
    
def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    mt5.initialize()
    
    
    #Parâmetros *********
    frames = [mt5.TIMEFRAME_D1, mt5.TIMEFRAME_M15, mt5.TIMEFRAME_M1]
    ativo = "USDJPY"
    quantidade_frames = 10000
    tamanho_entrada = 200
    volume = 0.01
    spread = 0.05
    taxa_dropout = 0
    volume = 0.01
    banca_inicial = 100
    #********************
    
    
    
    rates = list(copiar_rates(ativo, quantidade_frames, frames[1]))
    grade_de_entradas = criar_grade(rates)
    
    # Verificação inicial de ordem cronológica
    # if rates:
        # print("Primeiro rate:", timestamp_to_date(rates[0]['time']), rates[0])
        # print("Último rate:", timestamp_to_date(rates[-1]['time']), rates[-1])
        
    entradas = grade_de_entradas[0:tamanho_entrada]
    camadas = [len(entradas), 256, 128, 64, 32, 3]
    
    
    rn = RedeNeural(camadas, taxa_dropout, entradas, spread, ativo, volume, banca_inicial)
    #rn.carregar_pesos_bias("validacao 3")
    rn.rede_start(quantidade_frames, entradas, grade_de_entradas)
    
    
    rn.trade.calcular_winrate()
    rn.imprimir_infos_rede()
    
    
    plt.plot(rn.trade.historico_banca)
    mt5.shutdown()
    
    # dt = pd.DataFrame(rates)
    
    # rn.carregar_pesos_bias("pesos_bias2")
    
   
