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

def annotatePlot(mttf, reliability, rational=False):
	plt.annotate(
		't = {}'.format(Rational(mttf).limit_denominator(1000) if rational else round(mttf, 3)),
		xy = (mttf, reliability),
		xytext = (-20, 20),
		textcoords = 'offset points', ha = 'right', va = 'bottom',
		bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = .3),
		arrowprops = dict(arrowstyle = '-', connectionstyle = 'arc3, rad=0')).draggable()

#####################################################################
# MATHEMATICAL MODELS
#####################################################################

plt.subplot(211)
plt.title('Reliability (Mathematical models)')

models = []
models.append(ReliabilityModel(simplex(unitLambda), 'Simplex'))
models.append(ReliabilityModel(parallel(2, unitLambda), 'Parallel 2'))
models.append(ReliabilityModel(mOfN(3, 2, unitLambda), 'TMR'))
models.append(ReliabilityModel(mOfN(5, 3, unitLambda), '5MR'))
models.append(ReliabilityModel(mOfN(19, 10, unitLambda), '19MR'))

for model in models:
	(mttf, reliability) = model.calculateMttf()
	curve = model.generateCurve(timeArray)

	plt.plot(timeArray, curve, label=model.name)
	annotatePlot(Float(mttf), reliability, True)

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

voterFailureRate = failureRate/100
switchFailureRate = failureRate/100
auxRates = [voterFailureRate, switchFailureRate]

simulationSets = []
simulationSets.append((SimplexSystem(rates), 'Simplex'))
simulationSets.append((ParallelSystem(2, rates), 'Parallel 2'))
simulationSets.append((NMRSystem(3, 2, rates), 'TMR'))
simulationSets.append((NMRSystem(5, 3, rates), '5MR'))
simulationSets.append((NMRSystem(19, 10, rates, auxRates), '19MR'))

for simulation in simulationSets:
	start = time()

	template = simulation[0]
	label = simulation[1]

	(averages, (mttf, reliability)) = simulator.simulateAll(template)

	end = time()
	print(end - start)

	plt.plot(timeArray, averages, label=label)
	annotatePlot(mttf, reliability)

formatPlot()

#####################################################################
# PLOTTING
#####################################################################

plt.tight_layout()
plt.show();