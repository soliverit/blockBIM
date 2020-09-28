from .command import Command
class Modification(Command):
	def __init__(self, parameters):
		self.super().__init__(parameters)
	