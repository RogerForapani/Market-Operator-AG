# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 22:26:42 2024

@author: roger
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 11:39:00 2024

@author: roger
"""


        
class Individuo():
    def __init__(self,rede_neural,geracao=0):
        self.rede_neural = rede_neural
        self.geracao = geracao
        self.nota_avaliacao = 0
                
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
        
    def inicializa_populacao(self,tamanho_populacao):
        for i in range(tamanho_populacao):
            self.populacao.append(Individuo(Rede))
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

    tamanho_populacao = 20
    epocas = 2000
    probabilidade_mutacao = 0.003
    
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
            


    
    