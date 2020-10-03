from .base_environment 			import BaseEnvironment
from .sbem_model.sbem_inp_model import SbemInpModel
class SBEMEnvironment(BaseEnvironment):
	
	MODEL_CLASS 		= SbemInpModel
	MODEL_OBJ_PREFIX	= "Sbem"
	@staticmethod
	def RunSBEM(sbemModel):
		raise "SBEMEnvironment error: RunSBEM(static) is not defined"
	def __init__(self, name, modelID):
		##
		# Do parent constructor
		##
		super().__init__(name, modelID)
		##
		# Convert any Template/Wattage lighting values to efficacy
		##
		for zone in self.model.objects.filterByClass("%sZone" %(self.__class__.MODEL_OBJ_PREFIX)):
			zone.toChosen()
		##
		# Do model prep
		##
		res 					= self.getBaseEPCResults()
		self.SER				= res["SER"]
		self.BER				= res["BER"]
		self.model.setSER(self.SER)
	###################
	# Abstract stuff  #
	###################
	def printHelp(self):
		print("""
#################################################
#   DCE-MOOSBEM V1.0                            #
#                                               #
#   Welcome to DCE-MOOSBEM, the decentralised	#
#   common data environment for the MOOSBEM     #
#   gradient boosting regressor estimator for   #
#   the Simplified Building Energy Model        #
#                                               #
# Functions:                                    #
#   broadcast:	Generate a new block from       #
#               your changes                    #
#   connect:    Connect to the network          #
#   disconnect:	Disconnect from network	        #
#   exit:       Terminate the service           #
#   help:       Print this help message         #
#   list:       List objects                    #
#       Type:  HvacSystem, Construction, etc    #
#       Props: Comma delimited list of          #
#              SbemObject properties, AREA,     #
#              U-VALUE,<custom property>, etc   #
#   listBlocks: List all block names            #
#   modify:    Update the value of a property   #
#              an SbemObject with cost change   #
#       Name:     SBEM object name              #	
#       Property: SBEM object property name     #	
#       Value:    New value                     #
#       Cost:     Change to cost                #
#   printscript:  Print a script's content      #
#       Script:  Name of the script             #
#   ps:       As printscript                    #
#   script:   Run a script from the scripts dir	#
#      Name:     Name of the script             #
#################################################
		""")

	def printModel(self):
		print(" # SBEM:")
		print(" #  BER:\t\t%s" %(self.BER))
		print(" #  SER:\t\t%s" %(self.SER))
		print(" #  Current BER:\t%s" %(self.getCurrentPrediction()))
	def printBuilding(self):
		print(" # Building:")
		print(" #  Type:\t\t%s" %(self.model.general["B-TYPE"]))
		print(" #  Area:\t\t%s" %(self.model.area))
		print(" #  Location:\t%s" %(self.model.general["WEATHER"]))
		print(" #  Build Cost:\t%s" %(self.cost))
		print(" ###")