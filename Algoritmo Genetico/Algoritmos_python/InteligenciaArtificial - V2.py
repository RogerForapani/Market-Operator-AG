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
from concurrent.futures import ProcessPoolExecutor
import logging

# Configuração de logging
logging.basicConfig(filename='algoritmo_genetico.log', level=logging.INFO)


# Funções gerais ********************

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


# Classes **********************

class AlgoritmoGenetico():
    def __init__(self, tamanho_populacao):
        self.tamanho_populacao = tamanho_populacao
        self.populacao = []
        self.geracao = 0
        self.melhor_solucao = 0

    def inicializa_populacao(self, camadas, taxa_dropout, entradas, spread, moeda, volume, banca, geracao):
        for i in range(self.tamanho_populacao):
            rede = RedeNeural(camadas, taxa_dropout, entradas, spread, moeda, volume, banca, geracao)
            rede.mutacao(0.1)  # Introduzir variação inicial
            self.populacao.append(rede)
        self.melhor_solucao = self.populacao[0]

    def avaliar_ordenar_populacao(self):
        for i in range(len(self.populacao)):
            self.populacao[i].avaliacao()

        self.populacao = sorted(self.populacao,
                                key=lambda populacao: populacao.nota_avaliacao,
                                reverse=True)

    def melhor_individuo(self, individuo):
        if individuo.nota_avaliacao > self.melhor_solucao.nota_avaliacao:
            self.melhor_solucao = individuo

    def soma_avaliacoes(self):
        soma = 0
        for rede in self.populacao:
            soma += rede.nota_avaliacao
        return soma

    def seleciona_pai(self, soma_avaliacao):
        pai = -1
        valor_sorteado = random.random() * (soma_avaliacao / 2)
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

    def resolver(self, taxa_mutacao, epocas, camadas, taxa_dropout, entradas, spread, ativo, volume, banca, quantidade_frames, grade_de_entradas, geracao):
        self.inicializa_populacao(camadas, taxa_dropout, entradas, spread, ativo, volume, banca, geracao)
        plot2 = []
        plt.ioff()
        plt.ion()
        fig, ax = plt.subplots()
        line, = ax.plot([], [], 'r-')
        ax.set_xlim(0, epocas)
        ax.set_ylim(0, 1)

        def update_plot(geracao, nota):
            plot2.append(nota)
            line.set_xdata(range(len(plot2)))
            line.set_ydata(plot2)
            ax.relim()
            ax.autoscale_view() 
            fig.canvas.draw()
            fig.canvas.flush_events()

        for geracao in range(epocas):
            print("Gen: ", geracao)
            print("Pop: ", len(self.populacao))

            with ProcessPoolExecutor() as executor:
                list(executor.map(lambda rede: rede.rede_start(quantidade_frames, entradas, grade_de_entradas), self.populacao))

            self.avaliar_ordenar_populacao()
            melhor_avaliacao = self.populacao[0].nota_avaliacao
            update_plot(geracao, melhor_avaliacao)
            self.melhor_individuo(self.populacao[0])
            soma_avaliacao = self.soma_avaliacoes()
            nova_populacao = []

            taxa_mutacao_atual = taxa_mutacao * (1 - (geracao / epocas))

            for individuos_gerados in range(0, self.tamanho_populacao, 2):
                pai1 = self.seleciona_pai(soma_avaliacao)
                pai2 = self.seleciona_pai(soma_avaliacao)
                filhos = self.populacao[pai1].crossover(self.populacao[pai2])

                nova_populacao.append(filhos[0].mutacao(taxa_mutacao_atual))
                nova_populacao.append(filhos[1].mutacao(taxa_mutacao_atual))

            self.populacao = list(nova_populacao)

        plt.ioff()
        plt.show()
        plt.plot(plot2)
        print("Melhor geração: %s" % (self.melhor_solucao.imprimir_infos_rede()))
        return self.populacao[0]


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
        self.valores = np.random.randn(linhas, colunas) * np.sqrt(2 / linhas)


class Bias:
    def __init__(self, tamanho):
        self.valores = np.zeros((tamanho, 1))


class RedeNeural:
    def __init__(self, camadas, taxa_dropout, entradas, spread, moeda, volume, banca, geracao):
        self.entradas = np.array(entradas).reshape(-1, 1)
        self.camadas = camadas
        self.geracao = geracao
        self.taxa_dropout = taxa_dropout
        self.bias = [Bias(camada) for camada in camadas[1:]]
        self.pesos = [Pesos(camadas[i + 1], camadas[i]) for i in range(len(camadas) - 1)]
        self.trade = Trade(spread, moeda, volume, banca)
        self.ultima_saida = []
        self.banca_inicial = banca
        self.nota_avaliacao = 0

    def crossover(self, outra_rede):
        filho1 = RedeNeural(self.camadas,
                            self.taxa_dropout,
                            self.entradas,
                            self.trade.spread,
                            self.trade.moeda,
                            self.trade.volume,
                            self.trade.banca,
                            self.geracao + 1)

        filho2 = RedeNeural(outra_rede.camadas,
                            outra_rede.taxa_dropout,
                            outra_rede.entradas,
                            outra_rede.trade.spread,
                            outra_rede.trade.moeda,
                            outra_rede.trade.volume,
                            outra_rede.trade.banca,
                            outra_rede.geracao + 1)

        for i in range(len(self.pesos)):
            corte = round(random.random() * len(self.pesos[i].valores))
            filho1.pesos[i].valores[:corte, :] = self.pesos[i].valores[:corte, :]
            filho1.pesos[i].valores[corte:, :] = outra_rede.pesos[i].valores[corte:, :]

            filho2.pesos[i].valores[:corte, :] = outra_rede.pesos[i].valores[:corte, :]
            filho2.pesos[i].valores[corte:, :] = self.pesos[i].valores[corte:, :]

        for i in range(len(self.bias)):
            corte = round(random.random() * len(self.bias[i].valores))
            filho1.bias[i].valores[:corte, :] = self.bias[i].valores[:corte, :]
            filho1.bias[i].valores[corte:, :] = outra_rede.bias[i].valores[corte:, :]

            filho2.bias[i].valores[:corte, :] = outra_rede.bias[i].valores[:corte, :]
            filho2.bias[i].valores[corte:, :] = self.bias[i].valores[corte:, :]

        return [filho1, filho2]

    def mutacao(self, taxa_mutacao):
        for i in range(len(self.pesos)):
            if random.random() < taxa_mutacao:
                self.pesos[i] = Pesos(self.pesos[i].valores.shape[0], self.pesos[i].valores.shape[1])
        for i in range(len(self.bias)):
            if random.random() < taxa_mutacao:
                self.bias[i] = Bias(len(self.bias[i].valores))
        return self

    def rede_start(self, quantidade_frames, entradas, grade_de_entradas):
        for i in range(quantidade_frames):
            self.entradas = np.array(grade_de_entradas[i]).reshape(-1, 1)
            self.ultima_saida = self.forward()
            if self.ultima_saida[0] > self.ultima_saida[1] and self.ultima_saida[0] > self.ultima_saida[2]:
                self.trade.comprar(self.entradas[-1][0])
            elif self.ultima_saida[1] > self.ultima_saida[0] and self.ultima_saida[1] > self.ultima_saida[2]:
                self.trade.vender(self.entradas[-1][0])
            self.trade.calcular_banca(self.entradas[-1][0])
            self.trade.fechar_posicao(self.entradas[-1][0])
        self.trade.calcular_winrate()

    def forward(self):
        ativacao = self.entradas
        for i in range(len(self.pesos)):
            z = np.dot(self.pesos[i].valores, ativacao) + self.bias[i].valores
            ativacao = self.relu(z)
            if self.taxa_dropout > 0:
                mask = np.random.binomial(1, self.taxa_dropout, size=ativacao.shape) / self.taxa_dropout
                ativacao *= mask
        return ativacao

    def relu(self, z):
        return np.maximum(0, z)

    def avaliacao(self):
        lucro = self.trade.banca - self.banca_inicial
        self.nota_avaliacao = lucro
        logging.info(f'Geração: {self.geracao}, Lucro: {lucro}, Winrate: {self.trade.winrate}')

    def imprimir_infos_rede(self):
        print("Rede: %s\nNota: %s\nWinrate: %s\nBanca: %s" % (self.geracao, self.nota_avaliacao, self.trade.winrate, self.trade.banca))
        logging.info(f'Rede: {self.geracao}, Nota: {self.nota_avaliacao}, Winrate: {self.trade.winrate}, Banca: {self.trade.banca}')
        return json.dumps(self.trade.historico_banca)


# Exemplo de utilização
if __name__ == "__main__":
    ativo = "EURUSD"
    volume = 1.0
    banca = 1000.0
    quantidade_frames = 100
    taxa_mutacao = 0.1
    epocas = 1000
    taxa_dropout = 0.1
    entradas = 5  # Número de entradas (e.g., open, high, low, close, volume)
    spread = 0.0001
    camadas = [entradas, 256, 128, 64, 32, 3]  # Camadas da rede neural

    rates = copiar_rates(ativo, quantidade_frames, mt5.TIMEFRAME_M1)
    grade_de_entradas = criar_grade(rates)

    ag = AlgoritmoGenetico(tamanho_populacao=50)
    melhor_rede = ag.resolver(taxa_mutacao, epocas, camadas, taxa_dropout, entradas, spread, ativo, volume, banca, quantidade_frames, grade_de_entradas, geracao=0)
    print("Melhor rede encontrada:")
    melhor_rede.imprimir_infos_rede()
