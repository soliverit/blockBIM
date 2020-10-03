from .sbem_object import SbemObject
class SbemCompliance(SbemObject):
	def __init__(self, sbemModel, json):
		super(self.__class__,self).__init__(sbemModel, json)
