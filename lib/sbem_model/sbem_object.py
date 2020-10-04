from ..dce_model_object import DCEModelObject
class SbemObject(DCEModelObject):
    def __init__(self, sbemModel, json):
        super().__init__(sbemModel, json)
	#Translate class name to SBEM object category
    @classmethod
    def sbemObjectCode(self):
        return self.codeRegSplit.sub(r'-\1', self.__name__.replace("Sbem","")).upper()
    @property
    def sbemCode(self):
        return self.__name__.replace("Sbem","").upper()