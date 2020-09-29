#Native
from time 				import time
from random 			import randint
#Project
from .commands.command	import Command
from hashlib			import sha1
##
# Block
##
class Block():
	@staticmethod 
	def Read(blockPath):
		with open(blockPath, "r") as blockFile:
			hash 		= blockFile.readline().strip()
			author 		= blockFile.readline().strip()
			costDelta	= float(blockFile.readline().strip())
			timestamp	= blockFile.readline().strip()
			updates		= []
			while(True):
				cmd = blockFile.readline().strip()
				if not len(cmd):
					break
				commandComponents 	= Command.CommandToArray(cmd)
				command				= Command.CommandFromArray(commandComponents)
				updates.append(command)
			
			return __class__(author, updates, costDelta, timestamp)
	@staticmethod
	def NameFromPath(path):
		return path.split("\\")[-1].split("/")[-1]
	def __str__(self):
		return"""
Hash:		%s
Time:		%s
CostDelta:	%s	
Data:
	%s
Filename:	%s
		"""			%(self.hash, 
						self.timestamp, 
						self.costDelta, 
						"\n\t".join([str(c) for c in self.commands]),
						self.filename)
		
	def __init__(self, author, commands, costDelta, timestamp):
		self.author		= author
		self.commands	= commands
		self.timestamp	= timestamp
	@property
	def hash(self):
		return str(sha1("".join([self.author,self.dataString]).encode("utf-8")).hexdigest()[0:25])
	@property
	def dataString(self):
		return "\n".join([str(command) for command in self.commands])
	@property
	def filename(self):
		return "%s.blk" %(self.hash)
	@property 
	def costDelta(self):
		cost = 0
		for command in self.commands:
			if command.alias == "modify":
				cost += command.cost
		return cost
	def writePath(self, path):
		return "%s%s" %(path, self.filename)
	def write(self, path):
		with open(self.writePath(path), "w") as blockFile:
			blockFile.write("%s\n%s\n%s\n%s\n" 
				%(self.hash, 
				self.author, 
				self.costDelta, 
				self.timestamp
				))
			blockFile.write(self.dataString)