##
# Server command
##
class Command():
	@staticmethod
	def CommandFromArray(parameters):
		if parameters[0].lower() == "modify":
			return Modification(parameters)
		else:
			return Common(parameters)
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
		return " ".join(["\"%s\"" %(str(value)) for value in self.parameters])
	@property
	def alias(self):
		return self.parameters[0]

class Common(Command):
	def __init__(self, parameters):
		super().__init__(parameters)
class Modification(Command):
	def __init__(self, parameters):
		super().__init__(parameters)
	@property
	def objectName(self):
		return self.parameters[1]
	@property
	def cost(self):
		return float(self.parameters[4])
	@property
	def property(self):
		return self.parameters[2]