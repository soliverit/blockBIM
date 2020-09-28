from glob import glob
class Receiver():
	BLOCKS_PATH = "blocks/"
	def __init__(self, envPath, modelID):
		self.envPath		= envPath
		self.modelID	= modelID
	def scan(self):
		return glob("%s*_%s/%s*" %(self.envPath, self.modelID, __class__.BLOCKS_PATH))
			