from .props import *
###### Feature ######
# Prop object with history tracking
class Feature(Prop):
	def __init__(self, key, value):
		super(self.__class__,self).__init__(key, value)
		self.history = []
	def setValue(self, value):
		self.history.append(self.val)
		self.val = self.getValueFromType(value)
		