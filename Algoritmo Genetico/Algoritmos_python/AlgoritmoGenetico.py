# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 11:39:00 2024

@author: roger
"""
import numpy as np
import matplotlib.pyplot as plt
from random import random
class Produto():
    def __init__(self,nome,espaco,valor):
        self.nome = nome
        self.espaco = espaco
        self.valor = valor
        
class Individuo():
    def __init__(self,espacos,valores,limite_espacos,geracao=0):
        self.espacos = espacos
        self.valores = valores
        self.limite_espacos = limite_espacos
        self.geracao = geracao
        self.espaco_usado = 0
        self.nota_avaliacao = 0
        self.geracao = geracao
        self.cromossomo = []
        for i in range(len(espacos)):
            if random() <0.5:
                self.cromossomo.append(0)
                
            else:
                self.cromossomo.append(1)
                
    def avaliacao(self):
        nota = 0
        soma_espacos = 0
        for i in range(len(self.cromossomo)):
            if self.cromossomo[i] == 1:
                nota += self.valores[i]
                soma_espacos += self.espacos[i]
        if soma_espacos > self.limite_espacos:
            nota = 1
        self.nota_avaliacao = nota
        self.espaco_usado = soma_espacos

    def crossover(self,outro_individuo):
        corte = round(random() * len(self.cromossomo))
        cromossomo_filho1 = outro_individuo.cromossomo[0:corte] + self.cromossomo[corte::]
        cromossomo_filho2 = self.cromossomo[0:corte] + outro_individuo.cromossomo[corte::]
        filhos = [Individuo(self.espacos, self.valores, self.limite_espacos,self.geracao+1),
                  Individuo(self.espacos, self.valores, self.limite_espacos,self.geracao+1)]
        filhos[0].cromossomo = cromossomo_filho1
        filhos[1].cromossomo = cromossomo_filho2
        return filhos
        
    def mutacao(self,taxa_mutacao):
        for i in range(len(self.cromossomo)):
            if random() < taxa_mutacao:
                if self.cromossomo[i]== 1:
                    self.cromossomo[i] = 0
                else:
                    self.cromossomo[i] = 1
      
        return self
        
        
        
        
class AlgoritmoGenetico():
    def __init__(self,tamanho_populacao):
        self.tamanho_populacao = tamanho_populacao
        self.populacao = []
        self.geracao = 0
        self.melhor_solucao = 0
    def inicializa_populacao(self,espacos,valores,limite_espacos):
        for i in range(tamanho_populacao):
            self.populacao.append(Individuo(espacos, valores, limite_espacos))
        self.melhor_solucao = self.populacao[0]
        
    def avaliar_ordenar_populacao(self):
        for i in range(len(self.populacao)):
            self.populacao[i].avaliacao()
        
        self.populacao = sorted(self.populacao,
                                key= lambda populacao: populacao.nota_avaliacao,
                                reverse=True)
    def melhor_individuo(self,individuo):
        if individuo.nota_avaliacao > self.melhor_solucao.nota_avaliacao:
            self.melhor_solucao = individuo
            
    def soma_avaliacoes(self):
        soma = 0
        for individuo in self.populacao:
            soma+=  individuo.nota_avaliacao
        return soma
    def seleciona_pai(self,soma_avaliacao):
        pai = -1
        valor_sorteado = random() * soma_avaliacao
        soma = 0
        i = 0
        while i < len(self.populacao) and soma < valor_sorteado:
            soma += self.populacao[i].nota_avaliacao
            pai += 1
            i += 1
        return pai
    def visualiza_geracao(self):
        melhor = self.populacao[0]
        print("G: %s -> valor: %s Espaço: %s Cromossomo: %s" % (self.populacao[0].geracao,
                                                                melhor.nota_avaliacao,
                                                                melhor.espaco_usado,
                                                                melhor.cromossomo))
    def resolver(self,taxa_mutacao,numero_geracoes,espacos,valores,limite_espacos):
        self.inicializa_populacao(espacos, valores, limite_espacos)
        plot2 =[]
        
        for geracao in range(numero_geracoes):
            self.avaliar_ordenar_populacao()
            plot2.append(self.populacao[0].nota_avaliacao)
            
            self.melhor_individuo(self.populacao[0])
            self.visualiza_geracao()
            soma_avaliacao = self.soma_avaliacoes()    
            nova_populacao = []
            for individuos_gerados in range(0,self.tamanho_populacao,2):
                pai1 = self.seleciona_pai(soma_avaliacao)
                pai2 = self.seleciona_pai(soma_avaliacao)
                
                filhos = self.populacao[pai1].crossover(self.populacao[pai2])
                nova_populacao.append(filhos[0].mutacao(taxa_mutacao))
                nova_populacao.append(filhos[1].mutacao(taxa_mutacao))
                
            self.populacao = list(nova_populacao)
        plt.plot(plot2)
        print("*Melhor geração: %s - Valor: %s - Espaço: %s*" % (self.melhor_solucao.geracao,
                                                                  self.melhor_solucao.nota_avaliacao,
                                                                  self.melhor_solucao.espaco_usado)) 
        return self.melhor_solucao.cromossomo
    
        
        
        
        
        
        
if __name__ == "__main__":
    lista_produtos = []
    lista_produtos.append(Produto("Geladeira Dako", 0.751, 999.90))
    lista_produtos.append(Produto("Iphone 6", 0.0000899, 2911.12))
    lista_produtos.append(Produto("TV 55' ", 0.400, 4346.99))
    lista_produtos.append(Produto("TV 50' ", 0.290, 3999.90))
    lista_produtos.append(Produto("TV 42' ", 0.200, 2999.00))
    lista_produtos.append(Produto("Notebook Dell", 0.00350, 2499.90))
    lista_produtos.append(Produto("Ventilador Panasonic", 0.496, 199.90))
    lista_produtos.append(Produto("Microondas Electrolux", 0.0424, 308.66))
    lista_produtos.append(Produto("Microondas LG", 0.0544, 429.90))
    lista_produtos.append(Produto("Microondas Panasonic", 0.0319, 299.29))
    lista_produtos.append(Produto("Geladeira Brastemp", 0.635, 849.00))
    lista_produtos.append(Produto("Geladeira Consul", 0.870, 1199.89))
    lista_produtos.append(Produto("Notebook Lenovo", 0.498, 1999.90))
    lista_produtos.append(Produto("Notebook Asus", 0.527, 3999.00))
    
    espacos = []
    valores = []
    nomes = []
    limite_espacos = 3
    tamanho_populacao = 20
    epocas = 2000
    probabilidade_mutacao = 0.003
    for produto in lista_produtos:
        espacos.append(produto.espaco)
        valores.append(produto.valor)
        nomes.append(produto.nome)
        
    
   
    ag = AlgoritmoGenetico(tamanho_populacao)
    resolver = ag.resolver(probabilidade_mutacao, epocas, espacos, valores, limite_espacos)
    
    
    
    
    
    # for e in range(epocas):
    #     ag.avaliar_ordenar_populacao()
    #     ag.melhor_individuo(ag.populacao[0])
    #     soma = ag.soma_avaliacoes()
    #     plot1.append(soma)
    #     plot2.append(ag.melhor_solucao.nota_avaliacao)
    #     nova_populacao = []
    #     for individuo in range(0,ag.tamanho_populacao,2):
    #         pai1 = ag.seleciona_pai(soma)
    #         pai2 = ag.seleciona_pai(soma)
            
    #         filhos = ag.populacao[pai1].crossover(ag.populacao[pai2])
    #         nova_populacao.append(filhos[0].mutacao(probabilidade_mutacao))
    #         nova_populacao.append(filhos[1].mutacao(probabilidade_mutacao))
            
    #         ag.populacao = list(nova_populacao)
            


    
    