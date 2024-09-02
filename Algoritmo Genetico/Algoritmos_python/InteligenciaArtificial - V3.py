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
import random
from datetime import datetime

def copiar_rates(ativo, num_rates, frame):
    rates = mt5.copy_rates_from_pos(ativo, frame, 0, num_rates)
    return rates

def criar_grade(rates):
    grade_percentil = []
    grade_de_entradas = []
    ultimo = rates[0]['close']
    for rate in rates:
        grade_percentil += [((rate['close'] / ultimo) -1)*100]
        grade_de_entradas += [rate['close']]
        ultimo = rate['close']
    #print(grade_de_entradas)
    #print(len(grade_percentil))
   # print(grade_percentil[-1])
    #print(grade_de_entradas[-2],grade_de_entradas[-1])
    grade_de_entradas.insert(0,0)
    grade_percentil.insert(0,0)
    return [grade_de_entradas,grade_percentil]


class Trade:
    def __init__(self, spread, moeda, volume, banca):
        self.spread = spread
        self.moeda = moeda
        self.volume = volume
        self.quantidade_de_operacoes = 1
        self.winrate = 0.1
        self.wins = 0
        self.soma_vitorias = 0
        self.soma_derrotas = 0
        self.loses = 0
        self.posicoes_abertas = []
        self.banca = banca
        self.banca_liquida = banca
        self.historico_banca = []
        
        
    def vender(self, valor_real):
        # print("Venda : %s" %(valor_real))
        self.posicoes_abertas.append([valor_real - self.spread, -1])
        self.quantidade_de_operacoes += 1

    def comprar(self, valor_real):
        # print("Compra : %s" %(valor_real))
        self.posicoes_abertas.append([valor_real + self.spread, 1])
        self.quantidade_de_operacoes += 1

    def calcular_banca(self, valor_atual):
        #print(valor_atual)
        #print(self.banca," ---- ",valor_atual)
        banca_atual = self.banca
        for posicao in self.posicoes_abertas:
            if posicao[1] == 1:
                
                self.banca_liquida = banca_atual + ((valor_atual - posicao[0]) *0.1/0.0001)
                
            else:
                self.banca_liquida = banca_atual + ((posicao[0] - valor_atual) *0.1/0.0001)
                

    def fechar_posicao(self, valor_atual):
        for posicao in self.posicoes_abertas:
            valor = valor_atual - posicao[0] if posicao[1] == 1 else posicao[0] - valor_atual
            self.banca += (valor * 0.1)/0.0001
            if valor > 0:
                self.soma_vitorias += (valor * 0.1)/0.0001
                self.wins += 1
            else:
                self.soma_derrotas += (valor * 0.1)/0.0001
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
        self.valores = np.random.randn(tamanho, 1) * 0.01

class RedeNeural:
    def __init__(self, camadas, taxa_dropout, entradas, spread, moeda, volume, banca,valores,geracao = 0):
        self.entradas = np.array(entradas).reshape(-1, 1)
        self.valores = valores
        self.camadas = camadas
        self.geracao = 0
        self.taxa_dropout = taxa_dropout
        self.bias = [Bias(camada) for camada in camadas[1:]]
        self.pesos = [Pesos(camadas[i+1], camadas[i]) for i in range(len(camadas)-1)]
        self.trade = Trade(spread, moeda, volume, banca)
        self.nota_avaliacao = 0.0
        self.ultima_saida = []
        
    def avaliacao(self):
        if self.trade.quantidade_de_operacoes == 1:
            self.nota_avaliacao = 1
        else:
            self.nota_avaliacao = (self.trade.soma_vitorias - (self.trade.soma_derrotas*-1) + (self.trade.banca*0.1)) * (1/(len(self.trade.posicoes_abertas)+1))
            if self.nota_avaliacao <=0:
                self.nota_avaliacao = 1
        # if self.trade.winrate == 0.5:
        
            # self.nota_avaliacao = (self.trade.banca)
          
        # else:
            # self.nota_avaliacao = (self.trade.winrate+1) * self.trade.banca
    
    def crossover(self,outra_rede,camadas,taxa_dropout,entradas,spread,moeda,volume,banca_inicial,valores,geracao):
        filho1 = RedeNeural(camadas, 
                              taxa_dropout, 
                              entradas, 
                              spread, 
                              moeda, 
                              volume, 
                              banca_inicial,
                              valores,
                              self.geracao+1)

        filho2 = RedeNeural(camadas, 
                              taxa_dropout, 
                              entradas, 
                              spread, 
                              moeda, 
                              volume, 
                              banca_inicial,
                              valores,
                              outra_rede.geracao+1)

        for i in range(len(self.pesos)):
            corte = round(random.random() * len(self.pesos[i].valores))
            filho1.pesos[i].valores[:corte,:] = self.pesos[i].valores[:corte,:]
            filho1.pesos[i].valores[corte:,:] = outra_rede.pesos[i].valores[corte:,:]
            
            filho2.pesos[i].valores[:corte,:] = outra_rede.pesos[i].valores[:corte, :]
            filho2.pesos[i].valores[corte:,:] = self.pesos[i].valores[corte:,:]
        for i in range(len(self.bias)):
            corte = round(random.random() * len(self.bias[i].valores))
            filho1.bias[i].valores[:corte,:] = self.bias[i].valores[:corte,:]
            filho1.bias[i].valores[corte:,:] = outra_rede.bias[i].valores[corte:,:]
            
            filho2.bias[i].valores[:corte,:] = outra_rede.bias[i].valores[:corte, :]
            filho2.bias[i].valores[corte:,:] = self.bias[i].valores[corte:,:]
 
        return [filho1,filho2]
    
    
    
    
    
    
    def salvar_pesos_bias(self, filename):
        data = {
            'pesos': [p.valores.tolist() for p in self.pesos],
            'bias': [b.valores.tolist() for b in self.bias]
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
            
            
    def mutacao(self,taxa_mutacao):
        
        for i in range(len(self.pesos)):
            if random.random() < taxa_mutacao:
                perturbacao = np.random.randn(*self.pesos[i].valores.shape) * taxa_mutacao
                self.pesos[i].valores += perturbacao

        for i in range(len(self.bias)):
            if random.random() < taxa_mutacao:
                perturbacao = np.random.randn(*self.bias[i].valores.shape) * taxa_mutacao
                self.bias[i].valores += perturbacao
        
        return self
        
        
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
        #print(self.ultima_saida)
        return entrada

    def operar_saida(self, valor_real):
        
        if self.ultima_saida[0, 0] > 0:
            self.trade.comprar(valor_real)
        if self.ultima_saida[1, 0] > 0:
            self.trade.vender(valor_real)
        if self.ultima_saida[2, 0] > 0:
            # print("Fechar : %s" %(valor_real))
            self.trade.calcular_banca(valor_real)
            self.trade.fechar_posicao(valor_real)
            
        if len(self.trade.posicoes_abertas) >=7:
            self.trade.fechar_posicao(valor_real)
        self.trade.calcular_banca(valor_real)
        

    def rede_start(self,quantidade_frames,entradas,grade_percentil,grade_de_valores):
        for i in range(0, quantidade_frames-(len(entradas)-2)):
            if i == 0:
                self.entradas = np.array(entradas).reshape(-1, 1)
                self.valores = np.array(self.valores).reshape(-1,1)
            else:
                entradas = grade_percentil[i:i+200]
                valores = grade_de_valores[i:i+200]
                self.valores= np.array(valores).reshape(-1,1)
                self.entradas = np.array(entradas).reshape(-1,1)
                print(self.entradas)
            
            # Verificação no loop principal
            # if i % 99 == 0:  # Verifica a cada 100 iterações
                # print(f"Iteração {i}, timestamp do último dado: {timestamp_to_date(rates[i]['time'])}")

            self.calcular_oculta()
            # print("Entrada : %s" %(self.entradas[-1][0]))
            # print("Valores : %s" % (self.valores[-1][0]))
            self.operar_saida(self.valores[-1][0])
            self.trade.calcular_winrate() # calclar winrate antes
            if self.trade.banca < 0:
                self.nota_avaliacao = 0
                break
            self.trade.historico_banca.append(self.trade.banca)
        
    def imprimir_infos_rede(self):
        print("Winrate:", self.trade.winrate)
        print("Banca final:", self.trade.banca)
        print("Quantidade de operações: ", self.trade.quantidade_de_operacoes)
        print("Vitorias: ", self.trade.wins)
        print("Derrotas: ", self.trade.loses)
    
def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')




class AlgoritmoGenetico():
    def __init__(self,tamanho_populacao,mutacao,epocas):
        self.tamanho_populacao = tamanho_populacao
        self.populacao = []
        self.geracao = 0
        self.melhor_solucao = 0
        self.epocas = epocas
        self.mutacao = mutacao
        
    def seleciona_pai(self,soma_avaliacao):
        pai = -1
        valor_sorteado = random.random() * (soma_avaliacao) *0.7
        soma = 0
        i = 0
        while i < len(self.populacao) and soma < valor_sorteado:
            soma += self.populacao[i].nota_avaliacao
            pai += 1
            i += 1
        return pai       
        
    def avaliar(self,quantidade_frames,entradas,grade_percentil,grade_de_valores):
        soma_aval = 0
        for pop in self.populacao:
            pop.rede_start(quantidade_frames,entradas,grade_percentil,grade_de_valores)
            pop.avaliacao()
            soma_aval += pop.nota_avaliacao
        return soma_aval
    def ordenar_rankear(self):
        self.populacao = sorted(self.populacao,
                                key= lambda populacao: populacao.nota_avaliacao,
                                reverse=True)
        
        if self.melhor_solucao.nota_avaliacao < self.populacao[0].nota_avaliacao:
            self.melhor_solucao = self.populacao[0]    
        
    
    def inicializa_populacao(self,camadas,taxa_dropout,entradas,spread,moeda,volume,banca,valores):
        pop = []
        for i in range(self.tamanho_populacao):
            pop.append(RedeNeural(camadas,taxa_dropout,entradas,spread,moeda,volume,banca,valores))
            # if i < 3:
            #     pop[i].carregar_pesos_bias("gloriosa_evolucao 4")
        self.populacao = pop
        self.melhor_solucao = self.populacao[0]
        
        

        
    def criar_mundo(self,camadas,taxa_dropout,entradas,spread,moeda,volume,banca,valores,quantidade_frames,grade_percentil,grade_de_valores):
        self.inicializa_populacao(camadas,taxa_dropout,entradas,spread,moeda,volume,banca,valores)
        print(self.epocas)
        for epoca in range(int(self.epocas)):
            print(epoca)
            soma_aval = self.avaliar(quantidade_frames,entradas,grade_percentil,grade_de_valores)
            self.ordenar_rankear()
            geracao = self.populacao[0].geracao
            nova_populacao = []
            self.populacao[0].imprimir_infos_rede()
            print("Avaliação RANK1: %s\nAvaliação RANK2: %s\nAvaliação RANK3: %s" %(self.populacao[0].nota_avaliacao,self.populacao[1].nota_avaliacao,self.populacao[2].nota_avaliacao))
            for individuos_gerados in range(0,self.tamanho_populacao,2):
                    pai1 = self.seleciona_pai(soma_aval)
                    pai2 = self.seleciona_pai(soma_aval)
                    
                    #parei aqui
                    filhos = self.populacao[pai1].crossover(self.populacao[pai2],camadas,taxa_dropout,entradas,spread,moeda,volume,banca,valores,geracao)
            
                    nova_populacao.append(filhos[0].mutacao(self.mutacao))
                    nova_populacao.append(filhos[1].mutacao(self.mutacao))
                    
            self.populacao = nova_populacao
        
        return self.populacao[0]    

 





if __name__ == "__main__":
    mt5.initialize()
    
    
    #Parâmetros *********
    frames = [mt5.TIMEFRAME_D1, mt5.TIMEFRAME_M15, mt5.TIMEFRAME_M1]
    ativo = "EURUSD"
    quantidade_frames = 50000
    tamanho_entrada = 200
    volume = 0.01
    spread = 0.00005
    taxa_dropout = 0.02
    volume = 0.01
    banca_inicial = 500
    grades = []
    
    #********************
    tamanho_populacao = 26
    mutacao = 0.20
    epocas = 1000
    
    
    inicial_1_2 = 1
    
    #********************
    
    
    
    rates = list(copiar_rates(ativo, quantidade_frames, frames[1]))
    grades = criar_grade(rates)
    grade_de_valores = grades[0]
    grade_percentil = grades[1]
    # Verificação inicial de ordem cronológica
    # if rates:
        # print("Primeiro rate:", timestamp_to_date(rates[0]['time']), rates[0])
        # print("Último rate:", timestamp_to_date(rates[-1]['time']), rates[-1])
        
    entradas = grade_percentil[0:tamanho_entrada]
    valores = grade_de_valores[0:tamanho_entrada]
    camadas = [len(entradas), 256, 128, 64, 32, 3]
    
    if inicial_1_2 == 1:
        rn = RedeNeural(camadas, taxa_dropout, entradas, spread, ativo, volume, banca_inicial,valores)
        rn.carregar_pesos_bias("gloriosa evolução 4.1")
        rn.rede_start(quantidade_frames, entradas, grade_percentil,grade_de_valores)
    else:
        ag = AlgoritmoGenetico(tamanho_populacao,mutacao,epocas)
        ag.criar_mundo(camadas
                        ,taxa_dropout
                        ,entradas
                        ,spread
                        ,ativo
                        ,volume
                        ,banca_inicial
                        ,valores
                        ,quantidade_frames,
                        grade_percentil,
                        grade_de_valores)
        
    #quantidade_frames,entradas,grade_percentil,grade_de_valores
    
    # rn.trade.calcular_winrate()
    # rn.imprimir_infos_rede()
    
    
    # plt.plot(rn.trade.historico_banca)
    # mt5.shutdown()
    
    # dt = pd.DataFrame(rates)
    
    # rn.carregar_pesos_bias("pesos_bias2")
    
   
