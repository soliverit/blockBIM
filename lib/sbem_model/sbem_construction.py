from .sbem_object		import SbemObject
from .sbem_wall 		import SbemWall

class SbemConstruction(SbemObject):
    def __init__(self, sbemModel, json):
        super(self.__class__,self).__init__(sbemModel, json)
    
    @property
    def area(self):
        return self.sbemModel.classifiedObjects[SbemWall].filterByProperty('CONSTRUCTION', self.name).sum('area')
    
    @property
    def exteriorArea(self):
        return self.sbemModel.classifiedObjects[SbemWall].filterByProperty('CONSTRUCTION', self.name).filterByProperty('isExterior', True).sum('area')
    
    @property
    def isActive(self):
        return self.area > 0
    
    @property
    def isExterior(self):
        return self.exteriorArea > 0
    
    @property
    def isActiveAndExterior(self):
        return self.isActive and self.isExterior
    
    @property
    def isRoof(self):
        searchResult = self.sbemModel.classifiedObjects[SbemWall].findByProperty("CONSTRUCTION", self.name)
        if searchResult is not None:          
            return searchResult["TYPE-ENV"] == "Roof"
        else:
            return False