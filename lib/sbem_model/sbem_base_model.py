from .sbem_hvac_system import *
from .sbem_general import *
from .sbem_compliance import *
from .sbem_construction import *
from .sbem_dhw_generator import *
from .sbem_glass import *
from .feature import *
import pandas as pd

class SbemBaseModel():
    ORIENTATIONS = ["NORTH", "NORTH-EAST", "EAST", "SOUTH-EAST", "SOUTH", "SOUTH-WEST", "WEST", "NORTH-WEST", "HORIZONTAL"]
    
    def __getitem__(self, key):
        if hasattr(getattr(self, key), '__call__'):
            return getattr(self, key)
        if key in self.__dict__:
            return self.__dict__[key]
        return self.__getattribute__(key)
        
    def __str__(self):
        string = ""
        for obj in self.objects:
            string += str(obj)
        return string
    def addSbemEpcObject(self,epcObject):
        self.epcObject
    def updateFeatures(self, features):
        for feature in features:
            self.features[feature] = self[feature]
    def addObject(self,object):
        if object not in self.objects:
            self.objects.append(object)
        if object.__class__ not in self.classifiedObjects:
            self.classifiedObjects[object.__class__] = SbemObjectSet()
        if object not in self.classifiedObjects[object.__class__]:
            self.classifiedObjects[object.__class__].append(object)
    def findObject(self, name):
        return self.objects.findObject(name)
    def findObjects(self,cls, name=False):
        if not self.__classifiedObejcts[cls]:
            return SbemObjectSet()
        return self.classifiedObjects[cls].findObjects(cls)
    def findObjectsBy(self,cls,prop,value):
        return self.classifiedObjects[cls].filterByProperty(prop, value)
    