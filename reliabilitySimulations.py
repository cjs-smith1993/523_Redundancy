import numpy as np
from random import randint
import copy

import time as t

FAILED = False
WORKING = True

class SimulationSystem:
	UPPER_BOUND = 10000

	def __init__(self, numComponents, probabilityOfFailure, probabilityOfRepair):
		self.numComponents = numComponents
		self.components = [WORKING for i in range(numComponents)]
		self.probabilityOfFailure = probabilityOfFailure
		self.probabilityOfRepair = probabilityOfRepair

	def eventHappened(self, probability):
		return randint(0, self.UPPER_BOUND) < probability*self.UPPER_BOUND

	def evolve(self, t):
		for idx, component in enumerate(self.components):
			if component is WORKING:
				if self.eventHappened(self.probabilityOfFailure):
					self.components[idx] = FAILED
			else:
				if self.eventHappened(self.probabilityOfRepair):
					self.components[idx] = WORKING

class SimplexSystem(SimulationSystem):
	def __init__(self, probabilityOfFailure, probabilityOfRepair):
		super(SimplexSystem, self).__init__(1, probabilityOfFailure, probabilityOfRepair)

	def isWorking(self):
		return self.components[0] is WORKING

class SeriesSystem(SimulationSystem):
	def __init__(self, numComponents, probabilityOfFailure, probabilityOfRepair):
		super(SeriesSystem, self).__init__(
			numComponents,
			probabilityOfFailure,
			probabilityOfRepair)

	def isWorking(self):
		return self.components.count(WORKING) == self.numComponents

class ParallelSystem(SimulationSystem):
	def __init__(self, numComponents, probabilityOfFailure, probabilityOfRepair):
		super(ParallelSystem, self).__init__(
			numComponents,
			probabilityOfFailure,
			probabilityOfRepair)

	def isWorking(self):
		return self.components.count(WORKING) > 0

class NMRSystem(SimulationSystem):
	def __init__(self, numComponents, requiredNumComponents, probabilityOfFailure, probabilityOfRepair):
		super(NMRSystem, self).__init__(
			numComponents,
			probabilityOfFailure,
			probabilityOfRepair)
		self.requiredNumComponents = requiredNumComponents

	def isWorking(self):
		return self.components.count(WORKING) >= self.requiredNumComponents

class Simulator:
	def __init__(self, numIterations, populationSize, timeArray):
		self.numIterations = numIterations
		self.populationSize = populationSize
		self.timeArray = timeArray

	def simulate(self, template):
		systems = [[copy.deepcopy(template) for x in range(self.populationSize)] for y in range(self.numIterations)]

		numWorking = np.zeros((self.numIterations, len(self.timeArray)))
		failTimes = []
		repairTimes = []

		start = t.clock()
		for iteration in range(self.numIterations):
			for time in range(len(self.timeArray)):
				numWorking[iteration][time] = 0
				for system in systems[iteration]:
					oldState = system.isWorking()
					system.evolve(time)
					isWorking = system.isWorking()
					numWorking[iteration][time] += isWorking

					if oldState == WORKING and not isWorking:
						failTimes.append(self.timeArray[time])
					elif oldState == FAILED and isWorking:
						repairTimes.append(self.timeArray[time])
		end = t.clock()
		print(end - start)

		averageNumWorking = list(map(lambda list: sum(list)/len(list), zip(*numWorking)))
		averageNumWorking = [x / self.populationSize for x in averageNumWorking]

		mttf = np.mean(failTimes)
		reliability = averageNumWorking[next(i for i in range(len(self.timeArray)) if self.timeArray[i] > mttf)]

		return (averageNumWorking, (mttf, reliability))