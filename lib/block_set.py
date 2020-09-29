#Native
from glob				import glob
from hashlib 			import sha1
from time				import time
#Project
from .block 			import Block
from .commands.command	import Command
##
# Block Set
##
class BlockSet():
	def __init__(self, path):
		self.path	= path
		self.blocks	= []
		self.unwrittenCommands = []
	def appendCommand(self, command):
		self.unwrittenCommands.append(command)
	def generateNextBlock(self, author):
		cost		= 0
		for object in self.unwrittenCommands:
			if object.alias == "modify":
				cost += object.cost
		block 		= Block(author, list(self.unwrittenCommands), cost, str(time()))
		block.write(self.path)
		self.blocks.append(block)
		
		##
		# Clear Command cache
		##
		self.unwrittenCommands = []
		return block
		
		
	##
	# Generate Cost for current state
	##
	def cost(self, withModifications=True):
		cost = 0
		for object in self.blocks:
			cost += object.costDelta
		if(withModifications):
			for command in self.unwrittenCommands:
				if command.alias == "modify":
					cost += command.cost
		return cost
	##
	# Parse a block from somewhere, add it and save it to
	# the blocks folder.
	##

	def parseBlock(self, path):
		if self.contains(Block.NameFromPath(path).replace(".blk", "")):
			return False
		block 	= Block.Read(path)
		block.write(self.path)
		self.blocks.append(block)
		return block
		
	##
	# Does set contain items with filename
	##
	def containsBlockFile(self, path):
		return self.contains(Block.NameFromPath(path).replace(".blk", ""))
	##
	# Set contains item with hash
	##
	def contains(self, hash):
		for block in self.blocks:
			if block.hash == hash:
				return True				
	##
	# Get block by name
	##
	def getBlockByName(self, name):
		for block in self.blocks:
			if name in block.name:
				return block