from ..dce_model_object import DCEModelObject
class SbemObject(DCEModelObject):
    def __init__(self, sbemModel, json):
        super().__init__(sbemModel, json)