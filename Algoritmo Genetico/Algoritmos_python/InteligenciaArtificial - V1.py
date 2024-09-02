# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 21:08:51 2024

@author: roger
"""
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import numpy as np
import json
from datetime import datetime
import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor


#Funções gerais ********************


def copiar_rates(ativo, num_rates, frame):
    rates = mt5.copy_rates_from_pos(ativo, frame, 0, num_rates)
    return rates

def criar_grade(rates):
    grade_de_entradas = []
    for rate in rates:
        grade_de_entradas += [[rate['open']], [rate['high']], [rate['low']], [rate['close']], [rate['tick_volume']]]
    return grade_de_entradas

def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


#Classes **********************

class AlgoritmoGenetico():
    def __init__(self,tamanho_populacao):
        self.tamanho_populacao = tamanho_populacao
        self.populacao = []
        self.geracao = 0
        self.melhor_solucao = 0
        
    def inicializa_populacao(self,camadas,taxa_dropout,entradas,spread,moeda,volume,banca_inicial,geracao):
        for i in range(self.tamanho_populacao):
            self.populacao.append(RedeNeural(camadas, taxa_dropout, entradas, spread, moeda, volume, banca_inicial,geracao))
        self.melhor_solucao = self.populacao[0]
        
    def avaliar_ordenar_populacao(self):
        for i in range(len(self.populacao)):
            self.populacao[i].avaliacao(banca_inicial)
        
        self.populacao = sorted(self.populacao,
                                key= lambda populacao: populacao.nota_avaliacao,
                                reverse=True)
        
    def melhor_individuo(self,individuo):
        if individuo.nota_avaliacao > self.melhor_solucao.nota_avaliacao:
            self.melhor_solucao = individuo
            
    def soma_avaliacoes(self):
        soma = 0
        for rede in self.populacao:
            soma+=  rede.nota_avaliacao
        return soma
    def seleciona_pai(self,soma_avaliacao):
        pai = -1
        valor_sorteado = random.random() * (soma_avaliacao/2)
        soma = 0
        i = 0
        while i < len(self.populacao) and soma < valor_sorteado:
            soma += self.populacao[i].nota_avaliacao
            pai += 1
            i += 1
        return pai
    def visualiza_geracao(self):
        melhor = self.populacao[0]
        melhor.imprimir_infos_rede()
        
    def resolver(self,taxa_mutacao,epocas,camadas,taxa_dropout,entradas,spread,ativo,volume,banca_inicial,quantidade_frames,grade_de_entradas,geracao):
        self.inicializa_populacao(camadas,taxa_dropout,entradas,spread,ativo,volume,banca_inicial,geracao)
        plot2 =[]
      
        # plt.ion()
        # fig, ax = plt.subplots()
        # line, = ax.plot([], [], 'r-')
        # ax.set_xlim(0, epocas)
      
        # def update_plot(geracao, nota):
            # plot2.append(nota)
            # if geracao % 10 == 0 :
                
            #     line.set_xdata(range(len(plot2)))
            #     line.set_ydata(plot2)
            #     ax.relim()
            #     ax.autoscale_view()
            #     fig.canvas.draw()
            #     fig.canvas.flush_events()
        for geracao in range(epocas):
            print("Gen: ",geracao)
            print("Pop: ",len(self.populacao))
            
            # with ThreadPoolExecutor() as executor:
            #     list(executor.map(lambda rede: rede.rede_start(quantidade_frames, entradas, grade_de_entradas), self.populacao))

            for rede in range(len(self.populacao)):
                self.populacao[rede].rede_start(quantidade_frames,entradas,grade_de_entradas)
            
            self.avaliar_ordenar_populacao()
            self.populacao[0].imprimir_infos_rede()
            # plot2.append(self.populacao[0].nota_avaliacao)
            # melhor_avaliacao = self.populacao[0].nota_avaliacao
            # update_plot(geracao,melhor_avaliacao)
            self.melhor_individuo(self.populacao[0])
            soma_avaliacao = self.soma_avaliacoes()    
            nova_populacao = []
            for individuos_gerados in range(0,self.tamanho_populacao,2):
                pai1 = self.seleciona_pai(soma_avaliacao)
                pai2 = self.seleciona_pai(soma_avaliacao)
                filhos = self.populacao[pai1].crossover(self.populacao[pai2],camadas,taxa_dropout,entradas,spread,ativo,volume,banca_inicial,geracao)
                
                nova_populacao.append(filhos[0].mutacao(taxa_mutacao))
                nova_populacao.append(filhos[1].mutacao(taxa_mutacao))
                
            self.populacao = list(nova_populacao)
        # plt.ioff()
        # plt.show()
        plt.plot(plot2)
        print("Melhor geração: %s" %(self.melhor_solucao.imprimir_infos_rede()))
        return self.populacao[0]    

 


class Trade:
    def __init__(self, spread, moeda, volume, banca,posicoes_abertas = []):
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
                print(posicao[1])
                print(valor_atual)
                self.banca += valor_atual - posicao[0]
                
            else:
                print(posicao[1])
                print(valor_atual)
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
    def __init__(self, camadas, taxa_dropout, entradas, spread, moeda, volume, banca_inicial, geracao):
        self.entradas = np.array(entradas).reshape(-1, 1)
        self.camadas = camadas
        self.geracao = geracao
        self.taxa_dropout = taxa_dropout
        self.bias = [Bias(camada) for camada in camadas[1:]]
        self.pesos = [Pesos(camadas[i+1], camadas[i]) for i in range(len(camadas)-1)]
        self.trade = Trade(spread, moeda, volume, banca_inicial)
        self.ultima_saida = []
        self.banca_inicial = banca_inicial
        self.nota_avaliacao = 0
        
    def crossover(self,outra_rede,camadas,taxa_dropout,entradas,spread,moeda,volume,banca_inicial,geracao):
        filho1 = RedeNeural(camadas, 
                              taxa_dropout, 
                              entradas, 
                              spread, 
                              moeda, 
                              volume, 
                              banca_inicial,
                              self.geracao+1)

        filho2 = RedeNeural(camadas, 
                              taxa_dropout, 
                              entradas, 
                              spread, 
                              moeda, 
                              volume, 
                              banca_inicial,
                              outra_rede.geracao+1)

        for i in range(len(self.pesos)):
            corte = round(random.random() * len(self.pesos[i].valores))
            filho1.pesos[i].valores[:corte,:] = self.pesos[i].valores[:corte, :]
            filho1.pesos[i].valores[corte:,:] = outra_rede.pesos[i].valores[corte:,:]
            
            filho2.pesos[i].valores[:corte,:] = outra_rede.pesos[i].valores[:corte, :]
            filho2.pesos[i].valores[corte:,:] = self.pesos[i].valores[corte:,:]
        for i in range(len(self.bias)):
            corte = round(random.random() * len(self.bias[i].valores))
            filho1.bias[i].valores[:corte,:] = self.bias[i].valores[:corte, :]
            filho1.bias[i].valores[corte:,:] = outra_rede.bias[i].valores[corte:,:]
            
            filho2.bias[i].valores[:corte,:] = outra_rede.bias[i].valores[:corte, :]
            filho2.bias[i].valores[corte:,:] = self.bias[i].valores[corte:,:]
            
        filho1.trade = Trade(spread, moeda, volume, banca_inicial)
        filho2.trade = Trade(spread, moeda, volume, banca_inicial)
        return [filho1,filho2]
    
        
        
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
        
        
    
    def avaliacao(self,banca_inicial):  
        # print("------------------")
        # print("Banca atual: ",self.trade.banca)
        # print("Banca incial: ",banca_inicial)
        self.nota_avaliacao = self.trade.banca
        #self.nota_avaliacao =  self.trade.banca - banca_inicial
        # print("Nota avaliação: ",self.nota_avaliacao)
        
        
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
        self.trade = Trade(self.trade.spread, self.trade.moeda, self.trade.volume, self.banca_inicial)
        for i in range(0, quantidade_frames):
            if i == 0:
                self.entradas = np.array(entradas).reshape(-1, 1)
            else:
                entradas = entradas[5:] + grade_de_entradas[i*5:(i*5)+5]
                self.entradas = np.array(entradas).reshape(-1, 1)

            self.calcular_oculta()
            # print(entradas[-2][0])
            self.operar_saida(entradas[-2][0])
            self.trade.historico_banca.append(self.trade.banca)
            if self.trade.banca <0:
                self.trade.calcular_winrate()
                self.imprimir_infos_rede()
        self.trade.calcular_winrate()
       
        
    def imprimir_infos_rede(self):
        print("Winrate:", self.trade.winrate)
        print("wins:", self.trade.wins)
        print("loses:", self.trade.loses)
        print("Banca final:", self.trade.banca)
        print("Quantidade de operações: ", self.trade.quantidade_de_operacoes)
        print("Numero da geração: ",self.geracao)
        print("Nota de avaliação; ",self.nota_avaliacao)
    

#TODO START

if __name__ == "__main__":
    mt5.initialize()
    
    
    #Parâmetros *********
    frames = [mt5.TIMEFRAME_D1, mt5.TIMEFRAME_M15, mt5.TIMEFRAME_M1]
    ativo = "EURUSD"
    quantidade_frames = 5000
    tamanho_entrada = 200
    volume = 0.01
    spread = 0.05
    taxa_dropout = 0.1
    volume = 0.01
    banca_inicial = 100
    geracao = 0
    tamanho_populacao = 20
    epocas = 20
    taxa_mutacao = 0.05
    #********************
    
    
    
    rates = list(copiar_rates(ativo, quantidade_frames, frames[1]))
    grade_de_entradas = criar_grade(rates)
    entradas = grade_de_entradas[0:tamanho_entrada]
    camadas = [len(entradas), 256, 128, 64, 32, 3]
    # rn = RedeNeural(camadas, taxa_dropout, entradas, spread, ativo, volume, banca_inicial,geracao)
    # rn.carregar_pesos_bias("validacao 3")
    # rn.rede_start(quantidade_frames, entradas, grade_de_entradas)
    
    ag = AlgoritmoGenetico(tamanho_populacao)
    better = ag.resolver(taxa_mutacao, epocas, camadas, taxa_dropout, entradas, spread, ativo, volume, banca_inicial,quantidade_frames,grade_de_entradas,geracao)
    
    
    len(ag.melhor_solucao.trade.historico_banca)
    plt.plot(ag.melhor_solucao.trade.historico_banca)
    # plt.plot(better.trade.historico_banca)
    mt5.shutdown()
    winrates = []
    bancas = []
    plt.ion()
    plt.plot(ag.melhor_solucao.trade.historico_banca)
    for individuo in ag.populacao:
        winrates.append(individuo.trade.winrate)
        bancas.append(individuo.trade.banca)

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(winrates)
    plt.title('Winrate por Geração')
    plt.xlabel('Geração')
    plt.ylabel('Winrate')
    
    plt.subplot(1, 2, 2)
    plt.plot(bancas)
    plt.title('Banca Final por Geração')
    plt.xlabel('Geração')
    plt.ylabel('Banca Final')
    
    plt.show()
    # dt = pd.DataFrame(rates)
    
    # rn.carregar_pesos_bias("pesos_bias2")
    
   
