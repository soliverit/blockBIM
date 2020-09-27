from .sbem_object import SbemObject

class SbemHvacSystemData(SbemObject):
    def __init__(self, sbemModel, json):
        super().__init__(sbemModel, json)