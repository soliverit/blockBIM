###
#	
###
#Native
from random 	import randint
from os.path 	import exists
from os			import mkdir
from os			import getcwd
from shutil		import rmtree
#Project
from lib.sbem_model.sbem_inp_model import SbemInpModel
############
#	Distributed 
############
class Environment():
	ROOT			= getcwd()
	SBEM_ROOT		= "%s/sbem/4.1.d/"
	#Environment instance directory base
	ENV_ROOT		= "%s/environments/" %(ROOT)
	#SbemInpModel projects directory base
	PROJECT_ROOT	= "%s/projects/" %(ROOT)
	SBEM_DIR_ALIAS	= "processing/"
	#SbemInpModel static file name
	MODEL_NAME		= "model.inp"
	##
	#	Build a Saleh-ML Environment (static)
	#
	#	return Environment
	##
	@staticmethod
	def BuildEnvironment():
		name 	= str(randint(10000000, 100000000000000))
		id		= __class__.GetModelID()
		env		= __class__(name, id)
		
		print("BuildEnvironment: Preparing environment repository")
		env.createRepository()
		print("BuildEnvironment: Creating local inp model copy")
		env.saveLocalModel()
		
		return env
	@staticmethod
	def runSBEM(sbemModel):
		pass
	##
	# Load SBEM model
	##
	@staticmethod
	def LoadSbemModel(path):
		model = False
		with open(path) as file:
			model = SbemInpModel(file.read())
		return model
	##
	# Get a valid Model ID (static)
	##
	@staticmethod
	def GetModelID():
		while(1):
			try:
				id = input("Enter project ID: ")
				if exists("%s%s/%s.inp" %(__class__.PROJECT_ROOT, id, id)):
					return id
				print("ID %s not found in PROJECT_ROOT '%s'" %(id, __class__.PROJECT_ROOT))
			except:
				print("ENV::GetModelID - Unknown Error")
	##
	# Initialise
	#
	#	name:		String
	#	modelID:	String [that can point to a valid model]
	##
	def __init__(self, name, modelID):
		self.name 		= "%s_%s" %(name, modelID)
		self.modelID	= modelID
		self.sbemModel	= __class__.LoadSbemModel(self.baseModelPath)
	##======================
	# Where the action happens!
	#
	# The main process
	##======================
	def run(self):
		try:
			print("FIRE")
		except:
			print("water")
	
	##
	# Save local copy of model
	##
	def saveLocalModel(self):
		with open(self.modelPath, "w") as model:
			model.write(str(self.sbemModel))
	##
	# Create repo if it doesn't exist
	##
	def createRepository(self):
		if not exists(self.path):
			mkdir(self.path)
			mkdir(self.processingPath)
	##
	# Cleanup after yourself
	##
	def cleanup(self):
		rmtree(self.path)
	##
	# Print summary
	##
	def printSummary(self):
		print("\t###")
		print("\t#Name:\t%s" %(self.name))
		print("\t# Directories:")
		print("\t#Path:\t%s" %(self.path))
		print("\t#Processing:\t%s" %(self.processingPath))
		print("\t#Local model:\t%s" %(self.modelPath))
		print("\t#Base model:\t%s" %(self.baseModelPath))
		print("\t#SBEM:\t%s" %(__class__.SBEM_ROOT))
		print("\t###")
		
		
	
	############ Properties ############
	
	##
	# Path properties
	##
	@property
	def path(self):
		return "%s%s/" %(__class__.ENV_ROOT, self.name)
	@property
	def processingPath(self):
		return "%s%s" %(self.path, __class__.SBEM_DIR_ALIAS)
	@property
	def modelPath(self):
		return "%s%s" %(self.path, __class__.MODEL_NAME)
	@property    
	def baseModelPath(self):
		return "%s%s/%s.inp" %(__class__.PROJECT_ROOT,str(self.modelID), str(self.modelID))
	