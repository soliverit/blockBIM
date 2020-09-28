from .props import Props
import re 
import pandas as pd
from decimal import Decimal
#BASE OBJECT IN GENERAL, THOUGH CURRENT JUST AN SBEM base
#Offers general subscripted and dotted property access
class SbemObject():
    
    #A few objects can't directly translate from type to class name. Force a set name
    forcedSbemObjectCode = False
    #Directly property splitter, life's easier though...
    codeRegSplit = re.compile("(?<=.)([A-Z])")
    def __init__(self, sbemModel, json):
        #self.json = json
        self.name = json["name"]
        self.props = Props(json["props"])
        self.originalProps = Props(json["props"])
        #Model pointer, links objects 
        self.sbemModel = sbemModel
        if sbemModel:
            self.sbemModel.addObject(self)
    #get the class at with 2/3 off!
    def cls(self):
        return self.__class__
    #Convert to INP file object string
    def __str__(self):
        string = "\"" + self.name + "\" = " + self.sbemObjectCode() + "\n"
        for k, v in self.props.properties.items():
            toAdd = True
            if type(v.value) == Decimal:
                if v.value.is_nan():
                    toAdd = False
            elif type(v.value) == float or type(v) == int:
                if pd.isna(v.value):
                    toAdd = False
            elif type(v.value) == str:
                if v.value == 'NaN':
                    toAdd = False
            if toAdd:
                string += k + " = " + str(v) + "\n"
        return string + " ..\n\n"
    #General accessor, best thought of as the dotted accessor although subscripted runs
    # through here eventually
    def __getattr__(self,name):
        if name in vars(self.__class__):
            return getattr(self,name)
        if name in self.__dict__:
            return self.__dict__[name]
        if name in self.props:
            return self.props[name]
        if name == "area":
            return self.props.AREA
        if name == "originalProps":
            return self.__dict__[name]
        if name == "props":
            return self.props
        return None
    #Subscripted read access
    def __getitem__(self,name):
        return self.__getattr__(name)
    #Subscripted write access 
    def __setitem__(self, name, value):
        self.props[name] = value
    #Accommodation for "if propertyName in properties"
    def __contains__(self, name):
        return name in self.props is not None
    def setProp(self, key, value):
        self.props.setProp(key, value)
    def getProp(self, key):
        return self.props.getProp(key)
    #Translate class name to SBEM object category
    @classmethod
    def sbemObjectCode(self):
        return self.codeRegSplit.sub(r'-\1', self.__name__.replace("Sbem","")).upper()
    @property
    def sbemCode(self):
        return self.__name__.replace("Sbem","").upper()
	#Handy printer
    def print(self):
        print("Name:" + self.name)
        print("Area:" + str(self.area))
        print("Props:")
        for k, v in self.props.properties.items():
            print("%s\t%s" %(k, v))
    
    # Get an attribute safely
    def safeGet(self, name, default):
        result = self.__getattr__(name)
        
        return result if result is not None else default
