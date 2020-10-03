###
#	
###
#Native
from random 	import randint
from os.path 	import exists
from os			import mkdir
from os			import getcwd
from shutil		import rmtree, copyfile
from pandas		import read_csv
from time		import sleep
from sys		import stdout
from glob 		import glob
import _thread
from colorama 	import init, Fore, Back, Style
init()
#Project
from lib.machine			import Machine
from lib.block_set			import BlockSet
from lib.receiver			import Receiver
from lib.commands.command	import Command

############
#	Distributed 
############
class BaseEnvironment():
	##
	# Global 
	##
	ROOT			= getcwd()
	DATA_ROOT		= "%s/data/" %(ROOT)
	BEM_ENG_ROOT		= "%s/sbem/4.1.d/" %(ROOT)
	CONFIGS_ROOT	= "%s/configs/" %(ROOT)
	SCRIPTS_ROOT	= "%s/scripts/" %(ROOT)
	ENV_ROOT		= "%s/environments/" %(ROOT)
	#SbemInpModel projects directory base
	PROJECT_ROOT	= "%s/projects/" %(ROOT)
	#Blocks path
	BLOCKS_PATH		= "blocks/"
	#Feature input set
	FEATURES_PATH	= "%sfeatures.txt" %(CONFIGS_ROOT)
	##
	# Project path directory strings
	##
	SBEM_DIR_ALIAS	= "processing/"
	#SbemInpModel static file name
	MODEL_NAME		= "model.inp"
	#Default training data
	DEF_TRAIN_DATA	= "%stemp.csv" %(DATA_ROOT)
	
	#Block stuff
	GENESIS_NAME	= "2cfc750a06c2616ceb8facdf5.blk"
	GENESIS_PATH	= "%s%s" %(CONFIGS_ROOT, GENESIS_NAME)
	##
	# Machine learning stuff
	##
	TARGET			= "BER"
	PARAMETERS		= {"random_state": 1, "n_estimators":750}
	##
	# Scripts 
	##
	HOT_SCRIPT_PATH	= "shot_scripts/"
	##
	# Misc
	##
	INPUT_MESSAGE	= ">"
	
	##
	# Cheesy Flush console method
	##
	def FlushConsole():
		print("> ", end="")
		stdout.flush()
		
	##
	#	Build a Saleh-ML Environment (static)
	#
	#	return Environment
	##
	@classmethod
	def BuildEnvironment(self, withRegressor=False):
		name 	= str(randint(10000000, 100000000000000))
		id		= __class__.GetModelID()
		env		= self(name, id)
		print("\n################ Build Environment ###############")
		print("BuildEnvironment: Preparing environment repository")
		env.createRepository()
		print("BuildEnvironment: Creating local inp model copy")
		env.saveLocalModel()
		print("BuildEnvironment: Parsing feature list")
		with open(__class__.FEATURES_PATH) as featuresFile:
			for line in featuresFile:
				env.addFeature(line.strip())
		print("BuildEnvironment: Training Regressor")
		if withRegressor:
			env.buildRegressor(trainNow=True)
		print("BuildEnvironment: Finished")
		print("####################################################\n")
		
		return env
	##
	# Create a GradientBoostingRegressor
	##
	@staticmethod
	def CreateRegressor(inputDataPath):
		data = read_csv(inputDataPath)
		return Machine(
			data[int(len(data) * 0.5):],
			data[: int(len(data) * 0.5)],
			__class__.TARGET, 
			__class__.PARAMETERS
		)
	@classmethod
	def getModelClass(self):
		if not __class__.MODEL_CLASS:
			raise "%s error: MODEL_CLASS hasn't been defined\nThe expected value is a class that implements DCEModel"
	##
	# Load SBEM model
	##
	@classmethod
	def LoadModel(self, path):
		model = False
		with open(path) as file:
			print(self.__name__)
			print(self.__class__)
			model = self.MODEL_CLASS(file.read())
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
		self.name 				= "%s_%s" %(name, modelID)
		self.modelID			= modelID
		##
		# Lad SBEM model and translate lighting templates to Efficacy
		##
		self.model				= self.__class__.LoadModel(self.baseModelPath)
		
		self.features			= []
		self.blockSet			= BlockSet(self.blocksPath)	
		self.receiver			= Receiver(__class__.ENV_ROOT, self.modelID)
		#Kill processes
		self.exit				= False
		#Leave trail of your actions
		self.debug				= False
		#Listening for broadcasts
		self.connected			= True
		#Hot script thread
		self.hotScriptThread	= False
		#Network events thread
		self.networkEventsThread= False
		#Print message passed to self.printMessage
		self.silent				= False
		#
		self.regressor			= False
	##
	# Build instance regressor
	##
	def buildRegressor(self, trainNow=True):
		##
		# Build ML model if expected.
		#
		#	THIS might be done better but I'm no sure how
		#	at the moment. Wonder how many models will use it
		##
		self.regressor			= self.__class__.CreateRegressor(self.trainingDataPath)
		if trainNow:
			self.regressor.train()
	##
	# Pop a cap in the processor's... Terminate the environment
	##
	def terminate(self):
		print("Terminating environment")
		self.exit = True
		if not self.debug:
			self.cleanup()
	##
	# Interpret commands
	##
	def interpretCommand(self, command, track=True):
		
		if command.replace(" ","").replace("\t","").replace("\n","") == "":
			return False
		commandComponents = Command.CommandToArray(command)
		commandComponents[0] 	= commandComponents[0].lower()
		##
		# Terminate environment
		##
		validCommand	= False
		#Default Command type. Changed or nulled for custom or skip tracking
		if commandComponents[0] == "exit":
			self.terminate()
			track=False
		##
		# Print help
		##
		if commandComponents[0] == "help":
			self.printHelp()
		##
		# Modify object command
		##
		elif commandComponents[0] == "modify":
			if len(commandComponents) < 5:
				self.printMessage("Too few parameters for 'modify'. Expects 4", "Error")
				self.printMessage("'modify' expects (objectName, property, value, cost)", "Error")
			else:
				self.doModifyCommand(
					commandComponents[1],
					commandComponents[2],
					commandComponents[3],
					float(commandComponents[4]),
				)
				validCommand = True
		##
		# Disconnect
		##
		elif commandComponents[0] == "disconnect":
			self.printMessage("Disconnecting", "Network")
			self.connected 	= False
			track			= False
		##
		# Generate next block
		##
		elif commandComponents[0] == "broadcast":
			self.printMessage("Processing next Block", "Broadcast")
			generated 		= self.blockSet.generateNextBlock(self.name)
			track			= False
		##
		# Connect
		##
		elif commandComponents[0] == "connect":
			self.printMessage("Connecting", "Network")
			self.connected 	= True
			track			= False
		##
		# List the names of all blocks in the chain
		##
		elif commandComponents[0] == "listblocks":	
			for block in self.blockSet.blocks:
				print(block.filename)
				track		= False
		##
		# List all names of an object type, optional properties
		##
		elif commandComponents[0] == "list":
			self.printMessage("Listing '%s' objects" %(commandComponents[1].upper()))
			##
			# List objects and properties
			##
			objectSet = self.model.objects.filterByClass("Sbem%s" %(commandComponents[1]))	
			if len(objectSet) > 0:
				print("\n\t====== %s list ======")
				for object in objectSet.objects:
					self.printMessage(object.name,type="Name", pad="\t  ")
					if len(commandComponents) > 2:
						properties = commandComponents[2].split(",")
						for property in properties:
							self.printMessage(object[property], type=property, pad="\t\t")
				validCommand = True
			elif commandComponents[1][0].lower() == commandComponents[1][0]:
				self.printMessage("Object type shouldn't start with lowercase character")
		##
		# List static scripts
		##
		elif commandComponents[0] == "listscripts":
			print("\t### Listing static scripts ###")
			for path in glob(__class__.SCRIPTS_ROOT + "*"):
				print("\t%s" %(path.split("\\")[-1].split("/")[-1]))
			track=False
		##
		# Broadcast
		##
		elif commandComponents[0] == "broadcast":
			self.doBroadcast()
			track	= False
		##
		# Run an external script
		##
		elif commandComponents[0] == "script":
			if len(commandComponents) == 3:
				self.interpretCommand("ps %s" %(commandComponents[1]))
			self.doScript(commandComponents)
			track 			= False
			validCommand	= True
		##
		# Write message
		##
		elif commandComponents[0] == "chat":
			self.printMessage("\t%s SAYS: %s" %(self.name, " ".join(commandComponents[1: ])), type=Fore.WHITE +"Communication" + Fore.RESET, colour=Fore.YELLOW)
			track 			= True
			validCommand	= True
			
		##
		# Print the contents of a script
		##
		elif commandComponents[0] == "ps" or commandComponents[0] == "printscript":
			if len(commandComponents) < 2:
				self.printMessage("Print Script requires one input parameter", "Error")
				return False
			pScriptPath = self.createScriptPath(commandComponents[1])
			if not exists(pScriptPath):
				self.printMessage("Script '%s' for printing not found", "Error")
				return False
			with open(pScriptPath) as scriptFile:
				print("%s>>>>>> Print Script (%s)%s" %(Fore.WHITE, pScriptPath, Fore.RESET))
				
				for line in scriptFile:
					
					if line.strip().startswith("#"):
						fore = Fore.YELLOW
					else:
						fore = Fore.RESET
						
					print("%s>>%s\t%s%s%s" %(Fore.WHITE,
						Fore.RESET,
						fore,
						line.strip(),
						Fore.RESET))
			track = True
		__class__.FlushConsole()
		##
		# Record command:
		#
		# Commands recorded if 'commandClass' is still defined as one
		# of the Command subclasses
		##
		if(track and validCommand):
			self.blockSet.appendCommand(
				Command.CommandFromArray(commandComponents)
			)
		
	##
	# Create block for retrieval by anyone on the network
	##
	def doBroadcast(self):
		self.printMessage("Creating receivable Block", type="Broadcast", color=Fore.WHITE)
		self.blockSet.generateNextBlock()
	##
	#	Run scripts
	##	
	def doScript(self, scriptComponents):
		print("=== Running script: %s" %(scriptComponents[0]))
		if len(scriptComponents) < 2:
			self.printMessage("Script command missing script location", "Error")
			return False
		scriptPath = self.createScriptPath(scriptComponents[1])
		self.printMessage("Running script %s" %(scriptPath))
		if not exists(scriptPath):
			self.printMessage("Script not found %s" %(scriptPath), "ERROR")
			return False
		
		##
		# Read the script and process
		##
		with open(scriptPath) as script:
			for line in script:
				if not line.strip().startswith("#"):
					self.interpretCommand(line)
		print("======= /%s ======" %(scriptComponents[0]))
		return True
	def hotScriptHandler(self, threadName):
		print(Fore.WHITE + "\t### Hotscript event handler ###" + Fore.RESET)
		__class__.FlushConsole()
		##
		# Do until told to exit
		## 
		while(not self.exit):
			sleep(2)
			for path in glob(self.hotScriptsPath + "*"):
				self.printMessage("Found script", type="Hotscript", colour=Fore.CYAN)
				##
				# Read the script and process
				##
				with open(scriptPath) as hotScript:
					for line in hotScript:
						self.interpretCommand(line)
	##
	# Modify the building
	##
	def doModifyCommand(self, objectName, property, value, cost, track=True):
		
		self.printMessage("Modifying the building model")
		self.printMessage("Setting %s of object %s to %s" %(property, objectName, value))
		sbemObject 				= self.model.findObjectByName(objectName)
		sbemObject[property] 	= value	
		##
		# Print update
		##
		self.printMessage("%skgCO2/m²" %(self.getCurrentPrediction().round(1)),
			type="BER update",
			colour=Fore.WHITE)
		self.printMessage(self.cost,
			type="Cost update",
			colour=Fore.WHITE)
	##
	# Do network communication (Is Threaded somewhere)
	##
	def doNetworkEvents(self, threadName):
		__class__.FlushConsole()
		##
		# Continue handling network requests until told otherwise
		##
		while(not self.exit):
			##
			# Take a breather
			##
			sleep(2)
			##
			# Check if we're wanting to communicate
			##
			if not self.connected:
				continue
			##
			# Receiver and process blocks
			##
			#Listen for blocks on any node
			blockCandidates = self.receiver.scan()
			#Any new block(s) found
			newBlocks		= []
			if blockCandidates:
				##
				# Consider every distinct block, clone it if it's new
				##
				for candidate in set(blockCandidates):
					if not self.blockSet.containsBlockFile(candidate):
						newBlock = self.blockSet.parseBlock(candidate)
						newBlocks.append(newBlock)
						self.printMessage("New block found %s" %(newBlock.hash),pad="\n", force=True)
			##
			# Process new blocks
			##
			for newBlock in newBlocks:
				for command in newBlock.commands:
					self.interpretCommand(str(command), track=False)
			if len(newBlocks) > 0:
				self.printBuilding()
				self.printModel()
				__class__.FlushConsole()
			
				
	##======================
	# Where the action happens!
	#
	# The main process
	##======================
	def run(self):
		self.printMessage("""
		####                  ####
		# MOOSBEM interface v1.0 #
		###'                  ####
		""",type="", colour=Fore.WHITE)
		self.hotScriptThread 		= _thread.start_new_thread(self.hotScriptHandler, ("hot_script",))
		self.networkEventsThread	= _thread.start_new_thread(self.doNetworkEvents, ("netowrk_events",))
		while(not self.exit):
			command = input(">")
			self.interpretCommand(command,track=True)
	##
	#	Print a message to the console in <type>: <message> format
	##
	def printMessage(self, msg, colour=Fore.YELLOW,  force=False, pad=" ", type="Notification"):
		if self.silent and not force:
			return False
		if type == "Error":
			colour = Fore.RED
		print("%s%s:\t%s%s%s" %(pad,type, colour, msg, Fore.RESET))
	##
	# Get the predicted BER for the model in its current state 	
	##
	def getCurrentPrediction(self):
		return self.regressor.predict(self.model.extractFeatures(self.features))
	##
	# Add feature
	##
	def addFeature(self, feature):
		if feature not in self.features:
			self.features.append(feature)
	##
	# Get SER
	##
	def getBaseEPCResults(self):
		output = {"BER": False, "SER": False}
		with open(self.baseEpcModelPath) as epcFile:
			for line in epcFile:
				if line.strip().startswith("BER"):
					output["BER"] = float(line.split("=")[1].strip())
				if line.strip().startswith("SER"):
					output["SER"] = float(line.split("=")[1].strip())
				if output["BER"] and output["SER"]:
					return output
	##
	# Save local copy of model
	##
	def saveLocalModel(self):
		with open(self.modelPath, "w") as model:
			model.write(str(self.model))
	##
	# Create repo if it doesn't exist
	##
	def createRepository(self):
		if not exists(self.path):
			mkdir(self.path)
			mkdir(self.processingPath)
			mkdir(self.blocksPath)
			mkdir(self.hotScriptsPath)
			copyfile(__class__.GENESIS_PATH, self.genesisBlockPath)
	##
	# Generate Cost
	##
	@property 
	def cost(self):
		return self.blockSet.cost(True)
	##
	# Cleanup after yourself
	##
	def cleanup(self):
		rmtree(self.path)
	def printHelp(self):
		raise "%s error: printHelp has not been defined" %(__class__.__name__)
	##
	# Print summary
	##
	def printSummary(self):
		print("###")
		print(" # Name:\t\t\t%s" %(self.name))
		print(" # Directories:")
		print(" #  Path:\t\t%s" %(self.path))
		print(" #  Processing:\t\t%s" %(self.processingPath))
		print(" #  Hot scripts:\t%s" %(self.hotScriptsPath))
		print(" #  Local model:\t%s" %(self.modelPath))
		print(" #  Base model:\t\t%s" %(self.baseModelPath))
		print(" #  BEM Engine:\t\t%s" %(__class__.BEM_ENG_ROOT))
		print(" #  Train data:\t%s" %(self.trainingDataPath))
		self.printBuilding()
		self.printModel()
	def printModel(self):
		raise "%s error: printModel not defined"
	def printBuilding(self):
		raise "%s error: printBuilding not defined"
		
	##
	# Print features
	##
	def printFeatures(self):
		output 	= "###\n# Features:"
		temp	= "\t\t"
		for feature in self.features:
			temp += feature + ", "
			if len(temp) > 70:
				output += temp + "\n"
				temp = "\t\t"
		output += temp
		print(output)
	
	def createScriptPath(self, name):
		return "%s%s" %(self.SCRIPTS_ROOT, name)
	def createHotScriptPath(self, name):
		return "%s%s" %(self.hotScriptHandler, name)
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
	def blocksPath(self):
		return "%s%s" %(self.path, __class__.BLOCKS_PATH)
	@property
	def requestsPath(self):
		return "%s%s" %(self.path, __class__.REQUESTS_PATH)
	@property
	def genesisBlockPath(self):
		return "%s%s" %(self.blocksPath, __class__.GENESIS_NAME)
	@property
	def hotScriptsPath(self):
		return "%s%s" %(self.path, __class__.HOT_SCRIPT_PATH)
	@property
	def modelPath(self):
		return "%s%s" %(self.path, __class__.MODEL_NAME)
	@property    
	def baseModelPath(self):
		return "%s%s/%s.inp" %(__class__.PROJECT_ROOT,str(self.modelID), str(self.modelID))
	@property    
	def baseEpcModelPath(self):
		return "%s%s/%s_epc.inp" %(__class__.PROJECT_ROOT,str(self.modelID), str(self.modelID))
	@property
	def trainingDataPath(self):
		return "%s" %(__class__.DEF_TRAIN_DATA)