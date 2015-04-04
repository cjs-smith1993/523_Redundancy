import os
import struct

FAILED = False
WORKING = True

randomGenerator = open("/dev/urandom", "rb")
MAX_SHORT = 2**16

class SimulationSystem:
	UPPER_BOUND = 10000

	def __init__(self, numComponents, poolSize, sysRates):
		self.numComponents = numComponents
		self.components = [WORKING for i in range(numComponents)]
		self.poolSize = poolSize
		self.probabilityOfFailure = sysRates[0]
		self.probabilityOfRepair = sysRates[1]

	def eventHappened(self, probability):
		return struct.unpack("H", randomGenerator.read(2))[0] / MAX_SHORT < probability

	def evolve(self, t):
		if not self.isWorking():
			return
		for idx in range(len(self.components)):
			if self.components[idx] is WORKING:
				if self.eventHappened(self.probabilityOfFailure):
					if self.poolSize > 0:
						self.poolSize -= 1
					else:
						self.components[idx] = FAILED
			# else:
			# 	if self.eventHappened(self.probabilityOfRepair):
			# 		self.components[idx] = WORKING

class SimplexSystem(SimulationSystem):
	def __init__(self, poolSize, sysRates):
		super(SimplexSystem, self).__init__(1, poolSize, sysRates)

	def isWorking(self):
		return self.components[0] is WORKING

class SeriesSystem(SimulationSystem):
	def __init__(self, numComponents, poolSize, sysRates):
		super(SeriesSystem, self).__init__(numComponents, poolSize, sysRates)

	def isWorking(self):
		return self.components.count(WORKING) == self.numComponents

class ParallelSystem(SimulationSystem):
	def __init__(self, numComponents, poolSize, sysRates):
		super(ParallelSystem, self).__init__(numComponents, poolSize, sysRates)

	def isWorking(self):
		return self.components.count(WORKING) > 0

class NMRSystem(SimulationSystem):
	def __init__(self, numComponents, requiredNumComponents, poolSize, sysRates, auxRates):
		super(NMRSystem, self).__init__(numComponents, poolSize, sysRates)
		self.voter = WORKING
		self.switch = WORKING
		self.probabilityOfVoterFailure = auxRates[0]
		self.probabilityOfSwitchFailure = auxRates[1]*numComponents
		self.requiredNumComponents = requiredNumComponents

	def evolve(self, t):
		super(NMRSystem, self).evolve(t)
		if self.voter is WORKING:
			if self.eventHappened(self.probabilityOfVoterFailure):
				self.voter = FAILED
		if self.switch is WORKING:
			if self.eventHappened(self.probabilityOfSwitchFailure):
				self.switch = FAILED

	def isWorking(self):
		return (self.voter is WORKING and self.switch is WORKING
			and self.components.count(WORKING) >= self.requiredNumComponents)