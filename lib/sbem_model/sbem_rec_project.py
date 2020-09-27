from .sbem_object import SbemObject

class SbemRecProject(SbemObject):
    def __init__(self, sbemModel, json):
        super().__init__(sbemModel, json)