from .sbem_object 		import SbemObject
from .sbem_object_set 	import SbemObjectSet
from .sbem_window 		import SbemWindow
from .sbem_door 		import SbemDoor

class SbemWall(SbemObject):
    @property
    def isExterior(self):
        return self['TYPE'] == 'Exterior' or self['TYPE'] == 'Underground'
    @property
    def isConditioned(self):
        return self['TYPE'] == 'Conditioned adjoining space'
    @property
    def isFloor(self):
        return self['TYPE-ENV'] in self and self['TYPE-ENV'] == 'Floor or Ceiling'
    def __init__(self, sbemModel, json):
        super(self.__class__,self).__init__(sbemModel, json)
        self.windows = SbemObjectSet()
        self.doors = SbemObjectSet()
        self.cons = False
        self.Area = self.AREA * (self.MULTIPLIER if self.MULTIPLIER else 1)
        for window in json['windows']:
            self.windows.append(SbemWindow(sbemModel, window))
        for door in json['doors']:
            self.doors.append(SbemDoor(sbemModel, door))
    def __str__(self):
        string = super().__str__()
        for window in self.windows.objects:
            string += str(window)
        for door in self.doors.objects:
            string += str(door)
        return string
    @property
    def area(self):
        return self.Area
    @property
    def construction(self):
        if self.cons is False:
            self.cons = self.sbemModel.findObject(self['CONSTRUCTION'])
        return self.cons
    @property
    def conduction(self):
        return self.area * self.construction['U-VALUE']

