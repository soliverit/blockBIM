from .sbem_model import *
import re
from .sbem_hvac_system import *
from .sbem_general import *
from .sbem_compliance import *
from .sbem_construction import *
from .sbem_dhw_generator import *
# from .sbem_glass import *
class SbemInpModel(SbemModel):    
    OBJECT_MATCH_REGEX         = re.compile("^\s*\"([^\"]+)\"\s*=\s*([A-Z\-]+)([\s\S]*?)(?=\.\.(?=[\n\r\s]+))", re.MULTILINE)
    OBJECT_PROPERTY_REGEX    = re.compile("^\s*([0-9A-Z\-]+)\s*=\s*(.+)\s*$", re.MULTILINE)
    def __init__(self, text):
        self.classifiedObjects = {SbemObject:[],
                                  SbemHvacSystem:[],
                                  SbemZone:[],
                                  SbemWall:[],
                                  SbemWindow:[],
                                  SbemDhwGenerator:[],
                                  SbemGlass:[],
                                  SbemConstruction:[],
                                  SbemDoor:[]}
        
        self.objects = SbemObjectSet()
        self.dhws = SbemObjectSet()
        self.hvacs = SbemObjectSet()
        self.glasses = SbemObjectSet()
        self.constructions = SbemObjectSet()
        self.epcObject = None
        js = {"hvacs":[], "constructions":[], "glasses":[], "dhws":[]}
        curHvac = False
        curZone = False
        curWall = False
        
        hvacs = []
        isNumber = re.compile("^-?\d+\.?\d*$")
        for match in self.OBJECT_MATCH_REGEX.findall(text):
            # Fix issue whereby 
            
            obj = {"name":match[0],"props":{}}
            for prop in self.OBJECT_PROPERTY_REGEX.findall(match[2]):
                obj["props"][prop[0]] = prop[1] if not isNumber.match(prop[1]) else float(prop[1])
            obj["area"] = obj["props"]["AREA"] if "AREA" in obj["props"] else 0
            if match[1] == "GENERAL":
                self.general = SbemGeneral(self,obj)
                js["general"] = obj
            elif match[1] == "CONSTRUCTION":
                con = SbemConstruction(self,obj)
                self.constructions.append(con)
                self.classifiedObjects[SbemConstruction].append(con)
                js["constructions"].append(obj)
            elif match[1] == "GLASS":
                glass = SbemGlass(self,obj)
                self.glasses.append(glass)
                self.classifiedObjects[SbemGlass].append(glass)
                js["glasses"].append(obj)
            elif match[1] == "COMPLIANCE":
                self.compliance = SbemCompliance(self,obj)
                js["compliance"] = obj
            elif match[1] == "DHW-GENERATOR":
                if not self.dhws:
                    self.dhws = SbemObjectSet()
                dhw = SbemDhwGenerator(self, obj)
                self.dhws.append(dhw)
                self.objects.append(dhw)
                js["dhws"].append(obj)
            elif match[1] == "HVAC-SYSTEM":
                curHvac = obj
                curHvac["zones"] = []
                hvacs.append(curHvac)
                js["hvacs"].append(curHvac)
            elif match[1] == "ZONE":
                curZone = obj
                curHvac["zones"].append(curZone)
                curZone["walls"] = []
            elif match[1] == "WALL":
                curWall = obj
                curZone["walls"].append(curWall)
                curWall["windows"] = []
                curWall["doors"] = []
            elif match[1] == "WINDOW":
                curWall["windows"].append(obj)
            elif match[1] == "DOOR":
                curWall["doors"].append(obj)
            else:
                obj = SbemObject(self, obj)
                self.objects.append(obj)
                self.classifiedObjects[SbemObject].append(obj)
        super(self.__class__,self).__init__(js)

    @classmethod        
    def extractSpecificObjectType(self,text, key, delegate=SbemObject):
            pat = re.compile("^\s*\"([^\"]+)\"\s*=\s*%s([A-Z\-]+)([\s\S]*?)(?=\.\.)" %(key))
            output = SbemObjectSet()
            for match in pat.findall(text):
                props = {} 
                for prop in OBJECT_PROPERTY_REGEX.findall(match[2]):
                    props[prop[0]] = prop[1]
                output.append(delegate({"name": match[0], "props": props}))
            return output
            
            
        