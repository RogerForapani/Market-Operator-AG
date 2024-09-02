
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
def copiar_rates(ativo, data_final, num_rates, frame):
    rates = mt5.copy_rates_from(ativo, frame, data_final, num_rates)
    return rates

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
            else:
                self.banca += posicao[0] - valor_atual

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

if __name__ == "__main__":
    mt5.initialize()
    frames = [mt5.TIMEFRAME_D1, mt5.TIMEFRAME_M15, mt5.TIMEFRAME_M1]
    ativo = "EURUSD"
    data_final = time.time()
    quantidade_frames = 1000 #M15
    volume = 0.01
    spread = 0.05
    rates = list(copiar_rates(ativo, data_final, quantidade_frames, frames[1]))
    grade_de_entradas = [[rate[1], rate[2], rate[3], rate[4], rate[5]] for rate in rates]
    banco_dados = []
    entradas = grade_de_entradas[0:200]
    camadas = [len(entradas) * 5, 128, 64, 32, 3]
    taxa_dropout = 0
    
    rn = RedeNeural(camadas, taxa_dropout, entradas, spread, "GPDUSD", 0.01, 100)
    rn.carregar_pesos_bias('pesos_bias2')
    rn.calcular_oculta()
    rn.operar_saida(entradas[-1][0])
    
    for i in range(200, quantidade_frames - 5, 5):
        entradas = entradas[5:] + grade_de_entradas[i:i+5]
        rn.entradas = np.array(entradas).reshape(-1, 1)
        rn.calcular_oculta()
        rn.operar_saida(entradas[-2][0])
        print(entradas[-2][0])
        banco_dados.append(rn.trade.banca)
    plt.plot(banco_dados)
    rn.trade.calcular_winrate()
    print("Winrate:", rn.trade.winrate)
    print("Banca final:", rn.trade.banca)
    print("Quantidade de operações: ",rn.trade.quantidade_de_operacoes)