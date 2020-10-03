from .sbem_inp_model import SbemInpModel
from .sbem_epc_model import SbemEpcModel
##### Sbem Project ######
# Simple project for grouping inputs and outputs from SBEM
class SbemProject():
	def __init__(self, basePath):
		#Allow lazy declaration
		if basePath:
			self.sbemModel = SbemInpModel(open("%s/model.inp" %(basePath)).read())
			self.sbemEpcModel = SbemEpcModel(open("%s/model_epc.inp" %(basePath)).read())
			self.sbemModel.addEpcObject(self.sbemEpcModel.epcObject)
	#Deep clone the project
	def clone(self):
		output = self(None)
		output.sbemModel = SbemInpModel(str(self.sbemModel))
		output.sbemEpcModel = SbemEpcMode(str(self.sbemEpcModel))
		output.addEpcObject(output.sbemEpcModel.epcObject)
		return output