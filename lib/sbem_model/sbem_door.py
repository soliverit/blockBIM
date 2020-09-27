from .sbem_object import SbemObject

class SbemDoor(SbemObject):
    def __init__(self, sbemModel, json):
        super().__init__(sbemModel, json)
        self.cons = False
    
    @property
    def construction(self):
        if self.cons is False:
            self.cons = self.sbemModel.findObject(self['CONSTRUCTION'])
        return self.cons
