#Native
from time 				import time
from random 			import randint
#Project
from .commands.command	import Command
##
# Block
##
class Block():
	@staticmethod 
	def Read(blockPath):
		with open(blockPath, "r") as blockFile:
			hash 		= blockFile.readline().strip()
			author 		= blockFile.readline().strip()
			line 		= blockFile.readline().strip()
			costDelta	= float(line)
			timestamp	= blockFile.readline().strip()
			updates		= []
			while(True):
				cmd = blockFile.readline().strip()
				if not len(cmd):
					break
				commandComponents 	= __class__.CommandToArray(cmd)
				commandClass		= Command.ClassFromString(commandComponents[0])
				updates.append(commandClass(commandComponents))
			
			return __class__(author, blockPath, hash, updates, costDelta, timestamp)
	@staticmethod
	def NameFromPath(path):
		return path.split("\\")[-1].split("/")[-1]
	def __str__(self):
		print("""
Hash:		%s
Time:		%s
CostDelta:	%s	
Data:
	%s
		"""
			%(self.hash, self.timestamp, self.costDelta, "\n\t".join(self.data))
		)
	def __init__(self, author, filename, hash, data, costDelta, timestamp=time()):
		self.author		= author
		self.path		= filename
		self.data		= data
		self.hash		= hash
		self.costDelta	= float(costDelta)
		self.timestamp	= timestamp
	@property
	def filename(self):
		return __class__.NameFromPath(self.path)
	def write(self, path):
		with open(path, "w") as blockFile:
			blockFile.write("%s\n%s\n%s\n%s\n" 
				%(self.hash, 
				self.author, 
				self.costDelta, 
				self.timestamp
				))
			for modification in self.data:
				file.write("%s\n" %(str(data)))