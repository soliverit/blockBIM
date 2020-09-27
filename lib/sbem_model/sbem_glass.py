from .sbem_object import *

class SbemGlass(SbemObject):
    def __init__(self, sbemModel, json):
        super(self.__class__, self).__init__(sbemModel, json)
    
    @property
    def area(self):
        #Circular reference breaking classifiedObjects[SbemWindow], I think
        # Look into it when you get a chance, but it's like 4am so fuck it.
        return self.sbemModel.objects.filterByProperty("GLASS", self.name).sum("area")
        #return self.sbemModel.classifiedObjects[SbemWindow].filterByProperty("GLASS", self.name).sum("area")   # Circular import reference
    
    @property
    def isActive(self):
        return self.area > 0
