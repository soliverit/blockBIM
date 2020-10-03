from .sbem_object import SbemObject
class SbemGeneral(SbemObject):
	def __init__(self, sbemModel, json):
		super(self.__class__,self).__init__(sbemModel, json)
	@property
	def powerFactor(self):
		if self["ELEC-POWER-FACTOR"] == "<0.9":
			return 1
		if  self["ELEC-POWER-FACTOR"] == ">0.95":
			return 0.975
		return 0.99
