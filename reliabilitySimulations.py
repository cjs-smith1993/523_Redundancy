import numpy as np
from random import randint
import copy

from multiprocessing import Pool

FAILED = False
WORKING = True

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