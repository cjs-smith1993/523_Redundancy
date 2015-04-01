import numpy as np
import math
from sympy.mpmath import quad
from sympy.abc import t
from sympy.stats import cdf, Exponential
from sympy import lambdify

def simplex(l):
	return 1-cdf(Exponential('x', l))(t)

def series(n, l):
	return simplex(l)**n

def parallel(n, l):
	return 1-(1-simplex(l))**n

def mOfN(n, m, l):
	def nck(n, k):
		f = math.factorial
		return f(n)/(f(k)*f(n-k))

	return sum([nck(n, k)*(simplex(l)**k)*(1-simplex(l))**(n-k)	for k in range(m, n+1)])

class ReliabilityModel:
	def __init__(self, model, name):
		self.model = model
		self.name = name
		self.lambdified = lambdify(t, self.model)

	def calculateMttf(self):
		mttf = quad(self.lambdified, [0, np.inf])
		return (mttf, self.lambdified(mttf))

	def generateCurve(self, timeArray):
		return [self.lambdified(time) for time in timeArray]
