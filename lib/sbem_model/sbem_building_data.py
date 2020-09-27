from .sbem_object import SbemObject

class SbemBuildingData(SbemObject):
    def __init__(self, sbemModel, json):
        super().__init__(sbemModel, json)
