from .sbem_inp_model 				import *
from .sbem_object_set 				import *
from .sbem_epc 						import *
from .sbem_general 					import *
from .sbem_air_con_questionnaire	import *
from .sbem_rec_project 				import *
from .sbem_recommendation 			import *
from .sbem_building_data 			import *
from .sbem_hvac_system_data 		import *

class SbemEpcModel(SbemInpModel):
    def __init__(self, text):
        self.objects = SbemObjectSet()
        self.classifiedObjects = {SbemObject:SbemObjectSet(), SbemEpc:SbemObjectSet()}
        isNumber = re.compile("-?\d+\.?\d*")
        for match in self.OBJECT_MATCH_REGEX.findall(text):
            obj = {"name":match[0],"props":{}}
            for prop in self.OBJECT_PROPERTY_REGEX.findall(match[2]):
                # Match using regex
                numMatch = isNumber.match(prop[1])
                
                # Determine if it's a number only if the digits matched are the whole story
                propIsNum = False
                if numMatch is not None:
                    if numMatch[0] == prop[1]:
                        propIsNum = True
                
                obj["props"][prop[0]] = prop[1] if not propIsNum else float(prop[1])
            if match[1] == "EPC":
                sbemObj = SbemEpc(self, obj)
                self.epcObject = sbemObj
            elif match[1] == "GENERAL":
                sbemObj = SbemGeneral(self,obj)
            elif match[1] == "AIR-CON-QUESTIONNAIRE":
                sbemObj = SbemAirConQuestionnaire(self,obj)                
            elif match[1] == "REC-PROJECT":
                sbemObj = SbemRecProject(self,obj)                
            elif match[1] == "RECOMMENDATION":
                sbemObj = SbemRecommendation(self,obj)
            elif match[1] == "BUILDING-DATA":
                sbemObj = SbemBuildingData(self,obj)
            elif match[1] == "HVAC-SYSTEM-DATA":
                sbemObj = SbemHvacSystemData(self,obj)                
            else:
                sbemObj = SbemObject(self, obj)
                
            self.objects.append(sbemObj)
        