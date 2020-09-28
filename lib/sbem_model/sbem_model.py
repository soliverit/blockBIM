from .sbem_base_model import SbemBaseModel
from .sbem_hvac_system import SbemHvacSystem
from .sbem_general import SbemGeneral
from .sbem_compliance import SbemCompliance
from .sbem_construction import SbemConstruction
from .sbem_dhw_generator import SbemDhwGenerator
from .sbem_door import SbemDoor
from .sbem_glass import SbemGlass
from .sbem_object_set import SbemObjectSet
from .sbem_object_set_group import SbemObjectSetGroup
from .sbem_zone import SbemZone
from .sbem_wall import SbemWall
from .sbem_window import SbemWindow
from .feature import Feature
from .petites import readCSV
from decimal import Decimal

###
class SbemModel(SbemBaseModel):
    ORIENTATIONS = ["NORTH", "NORTH-EAST", "EAST", "SOUTH-EAST", "SOUTH", "SOUTH-WEST", "WEST", "NORTH-WEST", "HORIZONTAL"]
    
    def __getitem__(self, key):
        if hasattr(getattr(self, key), '__call__'):
            return getattr(self, key)
        if key in self.__dict__:
            return self.__dict__[key]
        return self.__getattribute__(key)
    def __init__(self, json):
        self.json = json
        self.objects = SbemObjectSet()
        self.classifiedObjects = {
            SbemConstruction: SbemObjectSet(),
            SbemGlass: SbemObjectSet(),
            SbemHvacSystem: SbemObjectSet(),
            SbemZone: SbemObjectSet(),
            SbemWall: SbemObjectSet(),
            SbemWindow: SbemObjectSet(),
            SbemDhwGenerator: SbemObjectSet(),
            SbemDoor: SbemObjectSet()
        }
        self.hvacs = SbemObjectSet()
        self.general = SbemGeneral(self,json["general"])
        self.compliance = SbemCompliance(self,json["compliance"])
        self.dhws = SbemObjectSet()
        self.constructions = SbemObjectSet()
        self.glasses = SbemObjectSet()    
        self.weath = False
        self.coolIrradianceKeys = False
 
        for construction in json["constructions"]:
            cons = SbemConstruction(self,construction)
            self.constructions.append(cons)
            self.objects.append(cons)
            self.classifiedObjects[SbemConstruction].append(cons)
        for glass in json["glasses"]:
            glass = SbemGlass(self,glass)
            self.glasses.append(glass)
            self.objects.append(glass)
            self.classifiedObjects[SbemGlass].append(glass)
        for hvac in json["hvacs"]:
            hvac = SbemHvacSystem(self, hvac)
            self.hvacs.append(hvac)
            self.objects.append(hvac)
            self.classifiedObjects[SbemHvacSystem].append(hvac)
        for dhw in json["dhws"]:
            dhw = SbemDhwGenerator(self,dhw)
            self.dhws.append(dhw)
            self.objects.append(dhw)
            self.classifiedObjects[SbemDhwGenerator].append(dhw)
        self.featuresToExtract = []
    def __str__(self):
        string = ""
        for obj in self.objects:
            if obj.__class__ is SbemHvacSystem:
                break
            string += str(obj)
        # Add DHWs if they exist
        if hasattr(self, 'dhws'):
            for dhw in self.dhws:
                string += str(dhw)
        # Add HVACs if they exist
        if hasattr(self, 'hvacs'):
            for hvac in self.hvacs:
                if not hvac.hidden:
                    string += str(hvac)
        return string
    def extractFeatures(self, features=None):
        features = features if features else self.featuresToExtract
        #################### READ ME!!!! Infinite loop craziness ##################
        #Modding the wrong array to infinity is a bitch, ain't it?
        #Update: Fuck knows, it's causing an infinite loop going over for feature in features
        # dirty fix for now.
        # for feature in list(features):
            # print(feature)

        self.features = {}
        i = 0
        while i < len(features):
            feature = features[i]
            if feature is not None:
                try:
                    value = self[feature]
                    if (value.__class__  == dict):
                        for k, v in value.items():
                            self.features[k] = Feature(k, v)
                    else:
                        self.features[feature] = Feature(feature, value)
                except AttributeError as e:
                    print(e)
            i += 1
        return self.features
    def switchToChosenLightingInputs(self):
        for zone in self.classifiedObjects[SbemZone].objects:
            zone.toChosen()
    def findObjectByName(self,name):
        return self.objects.findObject(name)
    ####
    #    IS: There a good reason for these not to use the new (relative to this)
    #        isActive property of these Sbem* classes?
    #    ANS:Yes, keeps Sbem* includes self-contained instead of leaking out everywhere
    ####
    def getActiveConstructions(self):
        return self.classifiedObjects[SbemConstruction].filterByProperty('isActiveAndExterior', True)
    def getActiveGlasses(self):
        return self.classifiedObjects[SbemGlass].filterByProperty('isActive', True)
    def getServicedHvacs(self):
        return self.classifiedObjects[SbemHvacSystem].filterByProperty('isHVACServiced', True)
    def getDedicatedDhws(self):
        return self.classifiedObjects[SbemDhwGenerator].filterOutByProperty('HEAT-GEN-TYPE', 'Using Central Heating boiler')
    
    # Get the relevant objects related to a class
    def getRelevantClassifiedObjects(self, SbemObjectClass):
        returnSbemObjectSet = None
        
        if SbemObjectClass == SbemConstruction:
            returnSbemObjectSet = self.getActiveConstructions()
        elif SbemObjectClass == SbemGlass:
            returnSbemObjectSet = self.getActiveGlasses()
        elif SbemObjectClass == SbemHvacSystem:
            returnSbemObjectSet = self.getServicedHvacs()
        elif SbemObjectClass == SbemDhwGenerator:
            returnSbemObjectSet = self.getDedicatedDhws()
        else:
            returnSbemObjectSet = self.classifiedObjects[SbemObjectClass]
        
        return returnSbemObjectSet
        
    
    
    ###
    #    Add SbemEpc object from _epc.inp file
    #        Object contains BER, TER, SER
    ###
    def addEpcObject(self,epcObject):
        self.epcObject = epcObject
        
    #SBEM weather location enumerated value
    @property
    def weatherKey(self):
        return self.general.WEATHER
    
    ###
    #    SER and BER methods have case toggled versions for convenience
    ###
    #Standard energy rating
    def setSER(self, ser):
        self.ser = ser
    # @property
    # def SER(self):
        # if not self.epcObject:
            # return None
        # return self.epcObject.ser()
    @property
    def area(self):
        return self.hvacs.sum("area")
    @property
    def SER(self):
        return self.ser
    
    #Building energy rating
    @property
    def BER(self):
        if not self.epcObject:
            return None
        return self.epcObject["BER"]
    
    @property
    def ber(self):
        return self.BER
    
    @property
    def heatedOrCooled(self):
        return self.hvacs.groupBy("isHVACServiced")
        
    @property
    def heatedHvacs(self):
        return self.hvacs.groupBy("isHeated")
    
    @property
    def cooledHvacs(self):
        return self.hvacs.groupBy("isCooled")
    
    @property
    def ventilatedHvacs(self):
        return self.hvacs.groupBy("hasMechanicalVentilation")
    
    @property
    def weather(self):
        if not self.weath:
            #self.weath = WeatherLocationData.find_by([["code", self.general["WEATHER"]]])
            
            self.weath = readCSV(file_path = 'data/db/weather_location_data.csv', column_to_filter = 'code', value_to_filter = self.general["WEATHER"])
        return self.weath
    #Feature functions
    
    @property 
    def heatedAreaRatio(self):
        return self.heatedHvacs[True].sum("area") / self.hvacs.sum("area")
    
    @property 
    def unconditionedAreaRatio(self):
        return self.heatedOrCooled[False].sum("area") / self.hvacs.sum("area")
    
    @property
    def cooledAreaRatio(self):
        return self.cooledHvacs[True].sum("area") / self.hvacs.sum("area")
    
    @property
    def ventilatedAreaRatio(self):
        return self.ventilatedHvacs[True].sum("area") / self.hvacs.sum("area")
    
    @property
    def solTrans(self):
        ### CHANGE TO COND = TRUE
        ### CHANGE TO AS U-VALUE WITH EEEFF DONE
        area  = self.classifiedObjects[SbemWindow].sum("area")
        output = self.heatedOrCooled[True].sum("areaWeightedGlazingSolTrans")
        return output / area if area > 0 else 0
    
    @property
    def wallToFloorRatio(self):
        wallArea = 0
        
        for wall in self.objects.filterByClassAndProperty(SbemWall, "TYPE", "Exterior").groupBy("TYPE-ENV")["Wall"]:
            wallArea += wall.area
        
        return wallArea / self.hvacs.sum("area")
    
    @property
    def windowToWallRatio(self):
        windowArea = 0
        wallArea = 0
        
        for wall in self.objects.filterByClassAndProperty(SbemWall, "TYPE", "Exterior").groupBy("TYPE-ENV")["Wall"]:
            windowArea += wall.windows.sum("area")
            wallArea += wall.area
        return windowArea / wallArea if wallArea > 0 else 0
    
    @property
    def internalGainsHeat(self):
        area = self.heatedHvacs[True].sum("area")
        return self.heatedHvacs[True].sum("internalGainsHeat") / area if area > 0 else 0
            
    @property
    def internalGainsCool(self):
        area = self.cooledHvacs[True].sum("area")
        return self.cooledHvacs[True].sum("internalGainsCool") / area if area > 0 else 0

    @property
    def opaqueConduction(self):
        area = self.heatedOrCooled[True].sum("exteriorWallArea")
        return self.heatedOrCooled[True].sum("areaWeightedOpaqueConduction") / area if area > 0 else 0
    
    @property
    def roofWallRatio(self):
        roof = self.classifiedObjects[SbemWall].filterByProperty( "TYPE-ENV", "Roof").sum("area")
        wall = self.classifiedObjects[SbemWall].filterByProperty( "TYPE", "Exterior").sum("area")
        return roof / wall if wall > 0 else 0
    
    @property
    def glazingConduction(self):
        area = self.classifiedObjects[SbemWindow].sum("area")
        return self.heatedOrCooled[True].sum("areaWeightedGlazingConduction") / area if area > 0 else 0
    
    @property
    def areaRatioOfDiabaticInternalPartitions(self):
        diabatic = self.heatedOrCooled[True].sum("areaOfDiabaticInternalPartitions")
        adiabatic = self.heatedOrCooled[True].sum("areaOfAdiabaticInternalPartitions")
        return diabatic / (adiabatic + diabatic + self.areaOfVerticalExternalSurface) if diabatic > 0 or adiabatic > 0 else 0
    
    @property
    def areaRatioOfAdiabaticInternalPartitions(self):
    
        diabatic = self.heatedOrCooled[True].sum("areaOfDiabaticInternalPartitions")
        adiabatic = self.heatedOrCooled[True].sum("areaOfAdiabaticInternalPartitions")
        return adiabatic / (adiabatic + diabatic + self.areaOfVerticalExternalSurface) if diabatic > 0 or adiabatic > 0 else 0
    
    @property
    def areaOfVerticalExternalSurface(self):
    
        return self.objects.filterByClassAndProperty(SbemWall,"TYPE", "Exterior").groupBy("TYPE-ENV")["Wall"].sum("area") 
    
    @property
    def areaRatioOfVerticalExternalSurface(self):
        area = self.areaOfVerticalExternalSurface 
        sum = area + self.heatedOrCooled[True].sum("areaOfDiabaticInternalPartitions") + self.heatedHvacs[True].sum("areaOfAdiabaticInternalPartitions")
        return area / sum if sum > 0 else 0

    ### CHANGE TO VOLUME
    @property
    def ventilationEnergyConsumption(self):
        objects = self.ventilatedHvacs[True] + self.heatedOrCooled[True]
        
        return objects.sum("ventilationPowerConsumption") / self.hvacs.sum("area")
    
    @property
    def hotWaterDemand(self):
        #### / AREA ####
        output = 0
        zonesByDhw = self.objects.findObjects(SbemZone).groupBy("DHW-GENERATOR")
        for dhw in self.dhws.objects:
            output += dhw.efficiency * zonesByDhw[dhw.name].sum("areaWeightedHotWaterDemand")
        return output / self.hvacs.sum("area")
    @property
    def irrVerticalHeat(self):
        groupSets = self.heatedHvacs[True]
        outputGroup = SbemObjectSetGroup("TYPE", SbemObjectSet)["Exterior"].groupBy("ORIENTATION")
        sumArea = 0
        sumIrr = 0
        for hvac in groupSets.objects:
            for key,set in hvac.wallsbyOrientation.sets.items():
                if key != "N/A" and key != None:
                    outputGroup.mergeSbemObjectSet(set)
        for key, set in outputGroup.sets.items():
            area = set.sum("area") 
            sumIrr += area * self.weather["irr_" + key.replace("-", "_").lower()]
            sumArea += area
        return sumIrr / sumArea if sumArea > 0 else 0
    @property
    def irrVerticalCool(self):
        groupSets     = self.cooledHvacs[True]
        outputGroup = SbemObjectSetGroup("TYPE", SbemObjectSet)["Exterior"].groupBy("ORIENTATION")
        sumArea     = 0
        sumIrr        = 0
        for hvac in groupSets.objects:
            for key,set in hvac.wallsbyOrientation.sets.items():
                if key != "N/A" and key != None:
                    outputGroup.mergeSbemObjectSet(set)
        for key, set in outputGroup.sets.items():
            area = set.sum("area") 
            sumIrr += area * self.weather["irr_" + key.replace("-", "_").lower()]
            sumArea += area
        return sumIrr / sumArea if sumArea > 0 else 0
        
    @property
    def irradiance(self):
        outputGroup = SbemObjectSetGroup("TYPE", SbemObjectSet)["Exterior"].groupBy("ORIENTATION")
        outArray = {}
        sumArea = 0
        area = {}
        for key in self.ORIENTATIONS:
            k = "irr_" + key.replace("-", "_").lower()
            outArray[k] = 0
        for hvac in self.heatedHvacs[True].objects:
            for key,set in hvac.wallsbyOrientation.sets.items():
                if key != "N/A" and key != None:
                    outputGroup.mergeSbemObjectSet(set)
        for key, set in outputGroup.sets.items():
            weatherKey = "irr_" + key.replace("-", "_").lower()
            outArray[weatherKey] = self.weather[weatherKey]#            set.sum("area", self.weather[weatherKey])
            sumArea += set.sum("area")
            area[weatherKey] = set.sum("area")
        for key, value in outArray.items():     
            outArray[key] =   value * (area[key] / sumArea ) if key in area and sumArea > 0 else 0
        return outArray

    @property
    def coolIrradiance(self):
        groupSets = self.cooledHvacs[True]
        outputGroup = SbemObjectSetGroup("TYPE", SbemObjectSet)["Exterior"].groupBy("ORIENTATION")
        outArray = {}
        sumArea = 0
        area = {}
        #Fill the gaps
        if not self.coolIrradianceKeys:
            self.coolIrradianceKeys = []
            for orientation in self.ORIENTATIONS:
                self.coolIrradianceKeys.append("cool_irr_" + orientation.replace("-", "_").lower())
                outArray[self.coolIrradianceKeys[-1]] = 0
                area[self.coolIrradianceKeys[-1]]         = 0
        else:
            for orientation in self.coolIrradianceKeys:
                outArray[orientation]     = 0
                area[orientation]         = 0
        if groupSets.sum("area") == 0:
            return outArray
        for hvac in self.cooledHvacs[True].objects:
            for key,set in hvac.wallsbyOrientation.sets.items():
                if key != "N/A" and key != None:
                    outputGroup.mergeSbemObjectSet(set)
        for key, set in outputGroup.sets.items():
            weatherKey         = "irr_" + key.replace("-", "_").lower()
            coolWeatherKey    = "cool_" + weatherKey
            outArray[coolWeatherKey] = self.weather[weatherKey]#            set.sum("area", self.weather[weatherKey])
            sumArea += set.sum("area")
            area[coolWeatherKey] = set.sum("area")
        for key, value in outArray.items():     
            outArray[key] = value * (area[key] / sumArea ) if sumArea > 0 else 0
        return outArray
    
    @property
    def lpd(self):
        area = self.classifiedObjects[SbemZone].sum("area")
        return self.classifiedObjects[SbemZone].sum("lpd", "area") / area if area > 0 else 0

    @property
    def q50(self):
        area = self.heatedOrCooled[True].sum("area")
        return self.heatedOrCooled[True].sum("q50") / area if area > 0 else 0

    @property
    def coolElectricEquivalentEfficiency(self):
        area = self.cooledHvacs[True].sum("area")
        return self.cooledHvacs[True].sum("electricEquivalentEfficiencyCool", "area") / area if area > 0 else 0
    
    @property 
    def heatElectricEquivalentEfficiency(self):
        area = self.heatedHvacs[True].sum("area")
        return self.heatedHvacs[True].sum("electricEquivalentEfficiencyHeat", "area") / area if area > 0 else 0
    
    @property
    def internalConduction(self):
        area = self.heatedHvacs[True].sum('area')
        
        if area > Decimal('0'):
            return self.heatedHvacs[True].sum('areaWeightedInternalConduction') / area
        else:
            return Decimal('0')

    @property
    def heatDesignLoad(self):
        # Get down to wall level
        output = Decimal('0')
        for hvac in self.heatedHvacs[True].objects:
            hvac_output = Decimal('0')
            for zone in hvac.zones.objects:
                zone_setpoint_delta = max([Decimal('0'), (zone.activity.heat_set_point - self.weather['heating_design_temp'])])
                for wall in zone.walls.objects:
                    if wall['TYPE'] == 'Unheated adjoining space':
                        hvac_output += wall.area * wall.construction['U-VALUE'] * zone_setpoint_delta
            output += hvac_output * hvac.electricEquivalentEfficiencyHeat
        
        area = self.heatedHvacs[True].sum('area')
        
        if area > Decimal('0'):
            return output / area
        else:
            return Decimal('0')

    @property
    def coolDesignLoad(self):
        # Get down to wall level
        output = Decimal('0')
        for hvac in self.cooledHvacs[True].objects:
            hvac_output = Decimal('0')
            for zone in hvac.zones.objects:
                zone_setpoint_delta = min([Decimal('0'), (zone.activity.cool_set_point - self.weather['cooling_design_temp'])])
                for wall in zone.walls.objects:
                    if wall['TYPE'] == 'Unheated adjoining space':
                        hvac_output += wall.area * wall.construction['U-VALUE'] * zone_setpoint_delta
            output += hvac_output * hvac.electricEquivalentEfficiencyCool
            
        area = self.cooledHvacs[True].sum('area')
        
        if area > Decimal('0'):
            return output / area
        else:
            return Decimal('0')


    
    
    
    
    
    
    
    
    
    
    
    
    
    