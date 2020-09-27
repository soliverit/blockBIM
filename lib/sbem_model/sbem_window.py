from .sbem_object import *
from .petites import importClassByName

class SbemWindow(SbemObject):
    def __init__(self, sbemModel, json):
        super(self.__class__,self).__init__(sbemModel, json)
        self.gls = False
    
    @property
    def glass(self):
        
        if self.gls is False:
            # Import SbemGlass by name to avoid circular reference
            obj = importClassByName(name = 'lib.sbem_model.sbem_glass.SbemGlass')
            
            self.gls = self.sbemModel.classifiedObjects[obj].findObject(self["GLASS"])
        return self.gls
    
    @property
    def conduction(self):
        # print(self.name + " " + self["GLASS"])
        # print(self.glass)
        return self.glass["U-VALUE"]
