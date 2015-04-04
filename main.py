import numpy as np
import matplotlib.pyplot as plt
from sympy import Rational, Float

from reliabilityModels import *
from reliabilitySimulations import *

from time import time

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
# SETUP
#####################################################################

plt.figure(num=1, figsize=(10,10))

unitLambda = 1
finalTime = 10*unitLambda
deltaTime = 0.01*unitLambda
timeArray = np.arange(0, finalTime, deltaTime)

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
models.append(ReliabilityModel(mOfN(99, 50, unitLambda), '99MR'))

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

simulationSets = []
simulationSets.append((SimplexSystem(deltaTime / unitLambda, 0), 'Simplex'))
simulationSets.append((ParallelSystem(2, deltaTime / unitLambda, 0), 'Parallel 2'))
simulationSets.append((NMRSystem(3, 2, deltaTime / unitLambda, 0), 'TMR'))
simulationSets.append((NMRSystem(5, 3, deltaTime / unitLambda, 0), '5MR'))
simulationSets.append((NMRSystem(99, 50, deltaTime / unitLambda, 0), '99MR'))

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