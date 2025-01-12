'''
計算グラフの可視化は、次のコマンドで行えます
$ python step22.py | dot -T png -o sample.png
'''

import numpy as np
from dezero import Variable
from dezero.utils import get_dot_graph


def goldstein(x0, x1):
    y = (1 + (x0 + x1 + 1)**2 * (19 - 14*x0 + 3*x0**2 - 14*x1 + 6*x0*x1 + 3*x1**2)) *\
        (30 + (2*x0 - 3*x1)**2 * (18 - 32*x0 + 12*x0**2 + 48*x1 - 36*x0*x1 + 27*x1**2))
    return y


x0 = Variable(np.array(1.0))
x1 = Variable(np.array(1.0))
y = goldstein(x0, x1)
y.backward()

x0.name = 'x0'
x1.name = 'x1'
y.name = 'y'
print(get_dot_graph(y))
