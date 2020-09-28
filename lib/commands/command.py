##
# Server command
##
class Command():
	@staticmethod
	def ClassFromString(name):
		if name == "modify":
			from .modification import Modification
			return Modification
		else:
			from .common import Common
			return Common
	##
	# Convert command string into array
	##
	@staticmethod
	def CommandToArray(command):
		output 			= []
		i 				= 0
		lastPostition	= 0
		while(i < len(command)):
			if command[i] == '"':
				i 				+= 1
				lastPostition 	= i 
				while command[i] != '"':
					i+= 1
				output.append(command[lastPostition: i])
				i 				+= 1
				lastPostition 	= i
			elif command[i] == ' ':
				output.append(command[lastPostition: i])
				lastPostition = i + 1
			i += 1
		output.append(command[lastPostition: i])
		
		return [ val.strip() for val in output]
	def __init__(self, parameters):
		self.parameters = parameters
	def __str__(self):
		return " ".join(["\"%s\"" %(value) for value in self.parameters])
	