import numpy as np
import matplotlib.pyplot as plt
from sympy import Rational, Float

from reliabilityModels import *
from simulationModels import *
from reliabilitySimulations import *

from time import time

#####################################################################
# SETUP
#####################################################################

plt.figure(num=1, figsize=(10,10))
colors = ['blue', 'green', 'red', 'cyan', 'purple']

unitLambda = 1
numLambda = 10
finalTime = numLambda*unitLambda
deltaTime = 0.01*unitLambda
timeArray = np.arange(0, finalTime, deltaTime)

#####################################################################
# HELPER FUNCTIONS
#####################################################################

def formatPlot():
	plt.xlim([0, 2*unitLambda])
	plt.ylim([0, 1])
	plt.xlabel(r'Time (multiple of $\lambda$)')
	plt.ylabel('Reliability')
	plt.legend()

def annotatePlot(i, mttf, reliability):
	plt.annotate(
		't = {}'.format(round(mttf, 3)),
		xy = (mttf, reliability),
		xytext = (0.9, 0.55-0.1*i),
		textcoords = 'axes fraction', ha = 'right', va = 'bottom',
		bbox = dict(boxstyle = 'round,pad=0.5', fc = colors[i], alpha = 0.6),
		arrowprops = dict(arrowstyle = '-', connectionstyle = 'arc3, rad=0')).draggable()

#####################################################################
# MATHEMATICAL MODELS
#####################################################################

plt.subplot(211)
plt.title('Reliability (Mathematical models)')

models = []
models.append(ReliabilityModel(simplex(unitLambda), 'Simplex'))
models.append(ReliabilityModel(mOfN(3, 2, unitLambda), 'TMR'))
models.append(ReliabilityModel(mOfN(5, 3, unitLambda), '5MR'))
models.append(ReliabilityModel(mOfN(19, 10, unitLambda), '19MR'))

for i, model in enumerate(models):
	(mttf, reliability) = model.calculateMttf()
	curve = model.generateCurve(timeArray)

	plt.plot(timeArray, curve, label=model.name)
	annotatePlot(i, Float(mttf), reliability)

formatPlot()

#####################################################################
# SIMULATIONS
#####################################################################

plt.subplot(212)
plt.title('Reliability (Monte Carlo Simulations)')

NUM_ITERATIONS = 10
POPULATION_SIZE = 100
simulator = Simulator(NUM_ITERATIONS, POPULATION_SIZE, timeArray)

failureRate = deltaTime/unitLambda
repairRate = 0*failureRate
rates = [failureRate, repairRate]

voterFailureRate = failureRate/10
switchFailureRate = failureRate/10
auxRates = [voterFailureRate, switchFailureRate]

simulationSets = []
simulationSets.append((SimplexSystem(rates), 'Simplex'))
simulationSets.append((NMRSystem(3, 2, rates, auxRates), 'TMR'))
simulationSets.append((NMRSystem(5, 3, rates, auxRates), '5MR'))
simulationSets.append((NMRSystem(19, 10, rates, auxRates), '19MR'))

for i, simulation in enumerate(simulationSets):
	start = time()

	template = simulation[0]
	label = simulation[1]

	(averages, (mttf, reliability)) = simulator.simulateAll(template)

	end = time()
	print(end - start)

	plt.plot(timeArray, averages, label=label)
	annotatePlot(i, mttf, reliability)

formatPlot()

#####################################################################
# PLOTTING
#####################################################################

plt.tight_layout()
plt.show();