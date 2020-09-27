from lib.sbem_model.sbem_object import *
class SbemEpc(SbemObject):
	def __init__(self, sbemModel, props):
		super(self.__class__,self).__init__(sbemModel, props)
	@property
	def ber(self):
		return self["BER"]
	def ser(self):
		return self["SER"] if self["SER"] is not None else 0
	def epc(self):
		return self["BER"] if self["SER"] is not None else self["BER"] / self["SER"] * 50