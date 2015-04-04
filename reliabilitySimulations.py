import numpy as np
from random import randint
import copy

import os
import struct

from multiprocessing import Pool

FAILED = False
WORKING = True

randomGenerator = open("/dev/urandom", "rb")
MAX_SHORT = 2**16

class SimulationSystem:
	UPPER_BOUND = 10000

	def __init__(self, numComponents, probabilityOfFailure, probabilityOfRepair):
		self.numComponents = numComponents
		self.components = [WORKING for i in range(numComponents)]
		self.probabilityOfFailure = probabilityOfFailure
		self.probabilityOfRepair = probabilityOfRepair

	def eventHappened(self, probability):
		return struct.unpack("H", randomGenerator.read(2))[0] / MAX_SHORT < probability

	def evolve(self, t):
		for idx in range(len(self.components)):
			if self.components[idx] is WORKING:
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

	def simulate(self, iteration, template):
		systems = [copy.deepcopy(template) for x in range(self.populationSize)]

		numWorking = np.zeros(len(self.timeArray))
		failTimes = []
		repairTimes = []

		for time in range(len(self.timeArray)):
			numWorking[time] = 0
			for system in systems:
				oldState = system.isWorking()
				system.evolve(time)
				isWorking = system.isWorking()
				numWorking[time] += isWorking

				if oldState is WORKING and not isWorking:
					failTimes.append(self.timeArray[time])
				elif oldState is FAILED and isWorking:
					repairTimes.append(self.timeArray[time])
		return (numWorking, failTimes, repairTimes)

	def simulateAll(self, template):
		pool = Pool(processes=self.numIterations)
		temp = [pool.apply_async(self.simulate, args=(i, template)) for i in range(self.numIterations)]
		results = [p.get() for p in temp]

		numWorking = [results[i][0] for i in range(self.numIterations)]
		averageNumWorking = list(map(lambda list: sum(list)/len(list), zip(*numWorking)))
		averageNumWorking = [x / self.populationSize for x in averageNumWorking]

		failTimes = [results[i][1] for i in range(self.numIterations)]
		averageFailTimes = list(map(lambda list: sum(list)/len(list), zip(*failTimes)))
		repairTimes = [results[i][2] for i in range(self.numIterations)]

		mttf = np.mean(averageFailTimes)
		reliability = averageNumWorking[next(i for i in range(len(self.timeArray)) if self.timeArray[i] > mttf)]

		return (averageNumWorking, (mttf, reliability))