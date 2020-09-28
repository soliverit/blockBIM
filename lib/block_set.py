#Native
from glob				import glob
#Project
from .block 			import Block
from .commands.common	import Common
##
# Block Set
##
from .commands.modification import Modification
class BlockSet():
	def __init__(self, path):
		self.path	= path
		self.blocks	= []
		self.unwrittenModifications = []
	def appendCommand(self, parameters):
		self.unwrittenModifications.append(Common(parameters))
	def generateNextBlock(self, author):
		hash 		= md5.new(self.path)
		filename	= self.path + hash
		cost		= 0
		data 		= ""
		for object in self.unwrittenModifications:
			if object.__class__ == Modification:
				cost += object.costDelta
			data += str(object) + "\n"
		block 		= Block(author, filename, hash, data, cost)
		block.write(filename)
		self.blocks.append(block)
		return block
		
		
	##
	# Generate Cost for current state
	##
	def cost(self, withModifications=True):
		cost = 0
		for object in self.blocks:
			cost += object.costDelta
		if(withModifications):
			for modification in self.unwrittenModifications:
				cost += modification.cost
		return cost
	##
	# Scan for new Blocks. Add any to the set and return them
	##
	def scan(self):
		newBlocks = []
		for blockPath in glob(self.path + "*"):
			blockName = blockPath.split("\\")[-1].split("/")[-1]
			if not self.contains(blockName):
				newBlock = Block.Read(blockPath)
				newBlocks.append(newBlock)
				self.blocks.append(newBlock)
		return newBlocks
	##
	# Parse a block from somewhere, add it and save it to
	# the blocks folder.
	##
	def parseBlock(self, path):
		block 	= Block.Read(path)
		name	= Block.NameFromPath(path)
		if self.contains(name):
			return False
		block.write(path)
		self.blocks.append(block)
		return block
		
	##
	#	Set has block with this filename
	##
	def contains(self, path):
		for block in self.blocks:
			if block.filename == Block.NameFromPath(path):
				return True
	##
	# Get block by name
	##
	def getBlockByName(self, name):
		for block in self.blocks:
			if name in block.name:
				return block