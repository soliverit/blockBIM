from .props 				import *
from .dce_object_set_group 	import DCEObjectSetGroup
###### DCE OBJECT SET ######
# Effectively a general object set (see dce_object.py)
# Store collection of DCEObjects to offer consistent storage
# and matrix operations
#
# IMPRTANT: For chaining this will return an empty set if no results were found.
#
# Object in set don't have to be the same type although some operations need those
# to common properties
class DCEObjectSet():
    #Create the empty set
    def __init__(self):
        self.objects = []
    #Subscriptable read access 
    def __getitem__(self, id):    
        if self.objects[id]:
            return self.objects[id]
        return self()
    #Implementation for the standard len(variable) function
    def __len__(self):
        return len(self.objects)
    #PROBABLY ALLOWS for a n b: type commands but I don't believe how it is described.
    # Test at some point, or just keep doing it the messy way, I don't care.
    def __iter__(self):
        return self.objects.__iter__()
    #Is object within the set
    def __contains__(self, test):
        #WHY NOT JUST: return Tru if obj in self.objects else False
        #    ANS: Not really the same thing though, are they?
        for obj in self.objects:
            if obj.name == test.name:
                return True
        return False
    
    # Add magic method so we can combine DCEObjectSets
    def __add__(self, other):
        returnDCEObjectSet = self.__class__()
        if self.__class__ == other.__class__:
            for obj in self.objects:
                returnDCEObjectSet.append(obj)
                
            for obj in other.objects:
                if obj not in returnDCEObjectSet:
                    returnDCEObjectSet.append(obj)
            
        return returnDCEObjectSet
    
    def __radd__(self, other):
        return self.__add__(other)        
    
    #Generate the sum of as value with optional weighting
    # For example: someSet.sum("light_lux", "area") would iterate over all items
    #  summing the product of the name and weight
    def sum(self,name,weight=False):
        sum = decimal.Decimal(0)
        for obj in self.objects:
            if weight.__class__ is not str:    
                w = weight if  weight is not False else decimal.Decimal(1)
            else:
                w = obj[weight] if obj[weight] is not None else 0
            temp = obj[name]
            sum += (temp if temp is not None else decimal.Decimal(0)) * w
        return sum
    #Does what it says on the tin - I think, never actually used it
    def weighted_average(self,name, weightKey="area"):
        value = 0
        weight = 0
        for obj in self.objects:
            value += (obj[name] if obj[name] is not None else decimal.Decimal(0)) * obj[weightKey]
            weight += obj[weightKey]
        return value / weight
    #Actually quite pleasant. general average
    def mean(self,name):
        return self.sum(name) / len(self.objects)
    #Middle value from the sorted set
    def median(self,name):
        values = []
        for obj in self.objects:
            values.append(obj[name] if obj[name] is not None else decimal.Decimal(0))
        values  = sorted(values)
        return values[int(len(values) / 2 - 1)] + values[int(len(values) / 2)] / 2 if len(values) % 2 == 0 else values[int((len(values) - 1) / 2 )]
    #DID SOMEONE SAY DUPLICATE FUNCTION (mean) but less cool?
    def average(self,name):
        output = 0
        for obj in self.objects:
            output += obj[name]
        return output / len(self)
    #Dot product of each object's named value with optional weighting
    def product(self,name, weight = False):
        output = 0
        for obj in self.objects:
            if weight.__class__ is not str:    
                w = weight if  weight is not False else decimal.Decimal(1)
            else:
                w = obj[weight] if obj[weight] is not None else 0
            temp = obj[name]
            output *= (temp if temp is not None else decimal.Decimal(0)) * w
        return output
    #Sum then divide two differing properties, including individual optional weighting
    def divideSums(self,name1, name2, weight1=False, weight2=False):
        sum2 = self.sum(name2, weight2)
        return  self.sum(name1, weight1) / sum2 if sum2 > 0 else decimal.Decimal(0)
    ###### Group by ######
    # Using any property available in the objects in the set, group by categorical values
    # For example groupBy("TYPE") for HVACS would create a set group for each TYPE
    # Access described in dce_object_set_group, basically group[<key>]
    def groupBy(self,name):
        outputs = DCEObjectSetGroup(name, self.__class__)
        for obj in self.objects:
            val = obj[name] if obj[name] is not None else "N/A"
            if val in outputs:
                outputs[val].append(obj)
            else:
                outputs[val] = self.__class__()
                outputs[val].append(obj)
        return outputs
    #Filter set by object class, returns new self()
    def filterByClass(self,cls):
        if not isinstance(cls, str):	
            cls = cls.__class__.__name__
        output = self.__class__()
        for obj in self.objects:
            if obj.__class__.__name__ == cls:
                output.append(obj)
        return output
    #Filter by class and property value
    def filterByClassAndProperty(self, cls, prop, val):
        output = self.__class__()
        for obj in self.objects:
            if obj.__class__ is cls and obj[prop] == val:
                output.append(obj)
        return output
    #Filter by property ignorant of class. If a property doesn't exist it's assumed a mismatch
    def filterByProperty(self,property,value):
        output = self.__class__()
        for obj in self.objects:
            if obj[property] == value:
                output.append(obj)
        return output
    
    # Return all objects which do not match this property:value combination
    def filterOutByProperty(self,property,value):
        output = self.__class__()
        for obj in self.objects:
            if obj[property] != value:
                output.append(obj)
        return output
    
    #Array-like push/append functionality. Won't permit duplicate insertion
    def append(self,object):
        for obj in self.objects:
            if obj.name == object.name:
                return False
        self.objects.append(object)
    #Find object by it's .name property. If objects don't have a name property they're excluded
    def findObject(self, name):
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None
    #DUPLICATE OF filterByClass
    def findObjects(self,cls):
        output = self.__class__()
        for obj in self.objects:
            if obj.__class__ is cls:
                output.append(obj)
        return output
    #Find the first instance by property
    def findByProperty(self, property, value):
        for obj in self.objects:
            if obj[property] == value:
                print(property)
                return obj
        return None
	#Find the first instance by property
    def findAllByProperty(self, property, value):
        for obj in self.objects:
            print(obj[property])
            if obj[property] == value:
                return obj
        return None
    
    # Find all instances which have these properties present, properties is a comma separated list of property keys or a list of property keys
    def findAllByPropertiesPresent(self, properties):
        if type(properties) == list:
            propsToCheck = properties
        else:
            propsToCheck = properties.split(',')
        
        output = []
        for obj in self.objects:
            addObj = True
            # Check all properties, if any missing then do not add this object to the output
            for property in propsToCheck:
                if obj[property] is None:
                    addObj = False
                    break                    
                    
            if addObj:
                output.append(obj)
                
        return output
    
    #Find the first instance of a class and property value
    def findByClassAndProperty(self, cls, property, value):
        for obj in self.objects:
            if obj.__class__ is cls and obj[property] == value:
                return obj
        return None
    #Print some debatably useful information
    def groupPrint(self):
        for k,v  in self.groupBy("__class__").sets.items():
            print("%s\t%s" %(k, len(v)))
    #Print about the objects not the sets.
    def print(self,name):
        for obj in self.objects:
            print(obj.name + ":\t" + str(obj.area) + "\t " + str(obj[name]))
        