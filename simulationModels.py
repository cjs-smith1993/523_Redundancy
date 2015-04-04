import os
import struct

FAILED = False
WORKING = True

randomGenerator = open("/dev/urandom", "rb")
MAX_SHORT = 2**16

class SimulationSystem:
	UPPER_BOUND = 10000

	def __init__(self, numComponents, sysRates):
		self.numComponents = numComponents
		self.components = [WORKING for i in range(numComponents)]
		self.probabilityOfFailure = sysRates[0]
		self.probabilityOfRepair = sysRates[1]

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
	def __init__(self, sysRates):
		super(SimplexSystem, self).__init__(1, sysRates)

	def isWorking(self):
		return self.components[0] is WORKING

class SeriesSystem(SimulationSystem):
	def __init__(self, numComponents, sysRates):
		super(SeriesSystem, self).__init__(numComponents, sysRates)

	def isWorking(self):
		return self.components.count(WORKING) == self.numComponents

class ParallelSystem(SimulationSystem):
	def __init__(self, numComponents, sysRates):
		super(ParallelSystem, self).__init__(numComponents, sysRates)

	def isWorking(self):
		return self.components.count(WORKING) > 0

class NMRSystem(SimulationSystem):
	def __init__(self, numComponents, requiredNumComponents, sysRates, auxRates):
		super(NMRSystem, self).__init__(numComponents, sysRates)
		self.requiredNumComponents = requiredNumComponents

	def isWorking(self):
		return self.components.count(WORKING) >= self.requiredNumComponents