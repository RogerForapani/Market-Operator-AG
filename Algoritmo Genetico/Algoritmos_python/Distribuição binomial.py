# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 20:19:44 2024

@author: roger
"""

import matplotlib.pyplot as plt

import numpy as np

from scipy.stats import binom

n = 500

p = 0.5

x = np.arange(0, n+1)

binomial = binom.pmf(k=x,n=n, p=p)

plt.bar(x, binomial)

plt.xlabel("x", fontsize=12)

plt.ylabel("Probabilidade", fontsize=12)

plt.xlim([-1, n+1])

plt.title("Distribuição Binomial, n={0}, p={1}".format(n, p),

          fontsize= 15)

plt.show()

for i in range(binomial.size):
    print("%s: %s" %(i,binomial[i]))


print("Hello world")