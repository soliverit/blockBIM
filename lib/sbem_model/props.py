import re
import decimal
import numpy as np
import pandas as pd
from .petites import automagicallyRound
#Semi-intelligent dict()
#Behaves like dictioary but automatically converts strings to floats if necessary
#TODO: Treat str ints as ints
#UPDATE TODO: Maybe not necessary any more. Although it's an important feature of the Ruby library
class Props():
    
    #Retrieve property from Props set
    def __getitem__(self,item):
        if item in self.properties:
            #return self.properties[item].value
            return self.properties[item].value
        return None
    
    #Length
    def __len__(self):
        return len(self.properties)
    #Set value, either new Prop or update Prop
    def __setitem__(self, item, value):
        if item not in self.properties:
            self.properties[item] = Prop(item, value)
        else:
            self.properties[item].setValue(value)
            
    #Return Prop value
    def __getattr__(self,name):
        if name in self.__dict__["properties"]:
            return self.__dict__["properties"][name].value
        if name in self.__dict__:
            return self.__dict__[name]
        if name in vars(self.__class__):
            return getattr(self,name)
        return None
    def __contains__(self, name):
        return name in self.properties
    #Initialise
    def __str__(self):
        output = ""
        for key,prop in self.properties.items():
            output += prop.key + ": " + str(prop.value) + " - " + str(prop.type) + "\n"
        return output
    def __init__(self, values={}):
        self.properties = dict()
        for k, v in  values.items():
            self.properties[k] = Prop(k, v)
    #Force Prop object replacement / retrieval
    def getProp(self, key):
        return self.properties[key]
    def setProp(self, key, value):
        self.properties[key] = value
#Single prop with key, value and type
#TODO: Add support for arrays, dicts and other mutable types
class Prop():
    strip_quotes = True
    #Match float / int from string - also catch missing preceding 0
    NUMERIC = re.compile('^-?\d*\.?\d*$')
    SANITISEDVALUE = re.compile('\"[^\"]+\"')     # Find word in-between quotes
    
    #Initialise
    def __init__(self, key, value):
        self.ky = key
        self.hasQuotes = False
        
        # type must be determined before value because type checks for quotes and so on
        self.typ = self.getValueType(value)
        self.val = self.getValueFromType(value)
        
    def __str__(self):
        if self.hasQuotes:
            return "\"" + str(self.value) + "\""
        return str(self.value)
    
    def __eq__(self, other):
        equal = False
        
        # First check they are the same class type
        if isinstance(other, self.__class__):
            equal = self.key == other.key and self.value == other.value and self.type == other.type and self.hasQuotes == other.hasQuotes
            
        return equal
    
    #Set the value, 
    def setValue(self, value):
        self.typ = self.getValueType(value)
        self.val = self.getValueFromType(value)

    @property
    #Return value
    def value(self):
        return self.val
    @property
    def key(self):
        return self.ky
    @property
    def type(self):
        return self.typ
    @property
    def databaseKey(self):
        return self.key.lower().replace("-", "_")
    @property
    def sbemKey(self):
        return self.key.upper().replace("_", "-")
    
    # Removes curly brackets and returns a list of their contents
    @property
    def sanitisedValues(self):
        if '{' in self.value and '}' in self.value:
            out = []
            for m in self.SANITISEDVALUE.findall(self.value):
                out.append(m.replace('"', ''))
                
            return out
            
        return [self.value]
    
    #Determine type from value
    def getValueType(self, value):
        if type(value) is not str: 
            if type(value) in [int, float, np.int16, np.int32, np.int64, np.float32, np.float64]:
                return decimal.Decimal
            return type(value)
        if self.NUMERIC.search(value):
            return decimal.Decimal
        if value[0] == "\"":
            self.hasQuotes = True
        return str
        
    #Set value, automatically deal with string to float conversion
    def getValueFromType(self, value):
        # Decimal doesn't play well with numpy data types so convert to Python ones first
        if value.__class__ in [np.int16, np.int32, np.int64]:
            value = int(value)
        if value.__class__ in [np.float32, np.float64]:
            value = float(value)
        
        if value.__class__ in [float, int]:
            try:
                return decimal.Decimal(automagicallyRound(value))
            except Exception as e:
                import pdb; pdb.set_trace()
        if value.__class__ is str and self.NUMERIC.search(value):
            return decimal.Decimal(automagicallyRound(value))
        if value.__class__ is str and self.__class__.strip_quotes and self.hasQuotes:
            return value[1:-1]
        return value
    
    @property
    def isNaN(self):
        if self.type == str:
            if pd.isnull(self.value):
                return True
        elif self.type == decimal.Decimal:
            if self.value.is_nan():
                return True
        return False
    
    @property
    def isFormula(self):
        if self.type == str:
            if self.value[0] == '{':
                return True
        return False
    
    
    
    