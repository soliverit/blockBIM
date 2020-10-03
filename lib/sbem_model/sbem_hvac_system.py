#Native
import decimal
#Project
from .sbem_object			import SbemObject
from .sbem_zone 			import SbemZone
from .sbem_object_set 		import SbemObjectSet
from .sbem_object_set_group import SbemObjectSetGroup
from .sbem_dhw_generator 	import SbemDhwGenerator
from ..petites 				import readCSV

class SbemHvacSystem(SbemObject):
    fuel_keys={'NaturalGas':'fuel_natural_gas',
            'DualFuelAppliances(Mineral+Wood)':'fuel_duel_fuel',
            'LPG':'fuel_lpg','Biomass':'fuel_biomass',
            'GridSuppliedElectricity':'fuel_grid_supplied_elec',
            'Biogas':'fuel_biogas','Oil':'fuel_oil',
            'Coal':'fuel_coal',
            'Anthracite':'fuel_anthracite',
            'SmokelessFuel(incCoke)':'fuel_smokeless',
            'GridDisplacedElectricity':'fuel_displaced',
            'WasteHeat':'fuel_waste_heat',
            'DistrictHeating':'fuel_dh'}
    
    FUEL_KEYS_SPACES = {
        "Natural Gas": "fuel_natural_gas",
        "LPG": "fuel_lpg",
        "Biogas": "fuel_biogas",
        "Oil": "fuel_oil",
        "Coal": "fuel_coal",
        "Anthracite": "fuel_anthracite",
        "Smokeless Fuel (inc Coke)": "fuel_smokeless",
        "Dual Fuel Appliances (Mineral + Wood)": "fuel_duel_fuel",
        "Biomass": "fuel_biomass",
        "Waste Heat": "fuel_waste_heat",
        "District Heating": "fuel_dh",
        "Grid Displaced Electricity": "fuel_displaced",
        "Grid Supplied Electricity": "fuel_grid_supplied_elec"
        }
    
    # Key is what the HVAC system calls it and value is what the DHW calls it
    PROTECTED_KEYS = {
        'HEAT-GEN-SEFF': 'HVAC-SYSTEM-EFF',
        'FUEL-TYPE': 'FUEL-TYPE',
        'HEAT-SOURCE': 'HEAT-SOURCE'
        }
    
    TERMINAL_UNIT_TYPES = ['Fan coil systems', 'Indoor packaged cabinets (VAV)']
    
    DECIMAL_ZERO = decimal.Decimal('0')
    
    CONVERSION_FACTORS = False
    def __init__(self, sbemModel, json):
        super(self.__class__,self).__init__(sbemModel,json)
        self.zones = SbemObjectSet()
        self.area = 0
        self.hidden = False
        self.linkedDhws = False
    
        for zone in json["zones"]:
            sbemZone = SbemZone(sbemModel, zone)
            self.zones.append(sbemZone)
            self.area += sbemZone.area
    def __str__(self):
        string = super().__str__()
        for zone in self.zones.objects:
            string += str(zone) 
        return string
    
    # Override for set prop so we can also update DHW systems at the same time
    def setProp(self, key, value):
        # Ensure we have a linked Dhw
        if self.hasLinkedDhw:
            # Try and see if there is a DHW equivalent to this key
            dhwKey = self.PROTECTED_KEYS.get(key, None)
            if dhwKey is not None:
                for dhw in self.getLinkedDhws():
                    dhw.setProp(dhwKey, value)
            
        # Still need to update the property for the HVAC system itself
        super().setProp(key, value)
    
    # Determine    
    @property
    def hasLinkedDhw(self):
        return self['DHW-SERVED-REF'] is not None
    
    # Return an SbemObjectSet containing any linked DHW systems
    def getLinkedDhws(self):
        if not self.linkedDhws:
            if self.hasLinkedDhw:
                self.linkedDhws = SbemObjectSet()
                for sv in self.props.getProp('DHW-SERVED-REF').sanitisedValues:
                    self.linkedDhws.append(self.sbemModel.classifiedObjects[SbemDhwGenerator].findObject(sv))
                
        return self.linkedDhws
    
    def getConversionFactor(self,type):
        if self.CONVERSION_FACTORS is False:
            self.CONVERSION_FACTORS = readCSV(file_path = 'data/db/emissions_factors.csv', column_to_filter = 'sbem_version', value_to_filter = '5.4.a')
            
        return self.CONVERSION_FACTORS[self.FUEL_KEYS_SPACES[type]]
    @property
    def conversionFactorHeat(self):
    
        if self.isHeated is False:
            return self.DECIMAL_ZERO
        if self.CONVERSION_FACTORS is False:
            self.CONVERSION_FACTORS = readCSV(file_path = 'data/db/emissions_factors.csv', column_to_filter = 'sbem_version', value_to_filter = '5.4.a')
        return self.CONVERSION_FACTORS[self.FUEL_KEYS_SPACES[self["FUEL-TYPE"]]]
    
    @property
    def conversionFactorCool(self):
        if self.isCooled is False:
            return self.DECIMAL_ZERO
        if self.CONVERSION_FACTORS is False:
            self.CONVERSION_FACTORS = readCSV(file_path = 'data/db/emissions_factors.csv', column_to_filter = 'sbem_version', value_to_filter = '5.4.a')
        return self.CONVERSION_FACTORS[self.FUEL_KEYS_SPACES[self["FUEL-TYPE-COOL"]]]
    
    @property
    def electricEquivalentEfficiencyHeat(self):
        return self.getConversionFactor("Grid Supplied Electricity") / self.conversionFactorHeat  * self["HEAT-SSEFF"]
    
    @property
    def electricEquivalentEfficiencyCool(self):
        return self.getConversionFactor("Grid Supplied Electricity") / self.conversionFactorCool  * self["COOL-SSEER"]
    @property
    def isCooled(self):
        return self["TYPE"] != "No Heating or Cooling" and self["COOL-SSEER"] is not None and self["COOL-GEN-EER"] is not None and self["COOL-GEN-SEER"] is not None and self["FUEL-TYPE-COOL"] is not None and self.area > 0
    
    @property
    def isHeated(self):
        return self["TYPE"] != "No Heating or Cooling" and self["HEAT-SSEFF"] and self.area > 0
    @property
    def isHVACServiced(self):
        return self.isHeated or self.isCooled
    @property
    def hasTerminalUnits(self):
        return self.TYPE == "Fan coil systems"
    ### Think about changing..............
    @property
    def hasMechanicalVentilation(self):
        return self["SFP"] is not None
    #ML Feature functions
    
    @property
    def exteriorWallAreaRatio(self):
        output = self.DECIMAL_ZERO
        for zone in self.zones:
            wallGroup = zone.walls.groupBy("isExterior")
            output += wallGroup[True].sum("area") / self.walls.sum("area")
        return output
    
    @property
    def q50(self):
        return decimal.Decimal(self.zones.sum("Q50-INF", "area")) / self.electricEquivalentEfficiencyHeat
    
    @property
    def internalGainsHeat(self):
        return self.zones.sum("internalGains", "area") / self["HEAT-SSEFF"] / self.electricEquivalentEfficiencyHeat
    
    @property
    def internalGainsCool(self):
        return self.zones.sum("internalGains", "area") / self["COOL-SSEER"] / self.electricEquivalentEfficiencyCool

    @property 
    def areaWeightedOpaqueConduction(self): 
        output = 0
        for zone in self.zones.objects:
            for wall in zone.walls.objects:
                output += wall.area * wall.construction["U-VALUE"] if wall.isExterior else 0
        ## * instead as per everything else    DONE    
        return output * self.electricEquivalentEfficiencyHeat 
    
    @property
    def exteriorWallArea(self):
        sos = SbemObjectSet()
        for zone in self.zones:
            for wall in zone.walls:
                if wall.isExterior:
                    sos.append(wall)
        return sos.sum("area")
    
    @property
    def externalEnvelopeConduction(self):
        q = 0
        for zone in self.zones.objects:
            q += zone.walls.groupBy("isExterior")[True].groupBy("TYPE-ENV")["Wall"].sum("conduction")
        return q * self.electricEquivalentEfficiencyHeat
    
    @property
    def areaOfDiabaticInternalPartitions(self):
        area = 0
        for zone in self.zones.objects:
            exts = zone.walls.groupBy("isExterior")
            if False in exts:
                #THIS COULD BE HANDLED WITHOUT THE CONDITION OR wall VAR
                walls = exts[False].groupBy("isConditioned")
                area += walls[False].sum("area") if False in walls else 0
        return area
    
    @property
    def areaOfAdiabaticInternalPartitions(self):
        area = 0
        for zone in self.zones.objects:
            exts = zone.walls.groupBy("isExterior")
            if False in exts:
                #THIS COULD BE HANDLED WITHOUT THE CONDITION OR wall VAR
                walls = exts[False].groupBy("isConditioned")
                area += walls[True].sum("area") if True in walls else 0
        return area
    
    @property
    def ventilationPowerConsumption(self):
        output = 0
        for zone in self.zones.objects:
            output += zone.airFlowRate * zone.area * ((zone.safeGet('SFP-TU', self.DECIMAL_ZERO) if self.TYPE in self.TERMINAL_UNIT_TYPES else zone.safeGet('VENT-SFP', self.DECIMAL_ZERO)) + zone.safeGet('VENT-SFP-EXH', self.DECIMAL_ZERO))
        
        return output
    
    @property 
    def areaWeightedGlazingConduction(self):
        output = 0
        for zones in self.zones:
            for wall in zones.walls:
                output += wall.windows.sum("conduction", "area")
        return output * self.electricEquivalentEfficiencyHeat
    
    @property
    def irradiance(self):
        return self.zones.groupBy("wallSurfaceArea")
    
    @property
    def wallsbyOrientation(self):
        wallSet = SbemObjectSetGroup("ORIENTATION", SbemObjectSet)
        for zone in self.zones.objects:
            for key, set in zone.walls.groupBy("ORIENTATION").sets.items():
                if key != "n/a":
                    wallSet.mergeSbemObjectSet(set)
        wallSet = wallSet.reGroupBy("TYPE")["Exterior"].groupBy("ORIENTATION")
        return wallSet
        
    @property
    def areaWeightedGlazingSolTrans(self):
        output = 0
        for zone in self.zones:
            for wall in zone.walls:
                for window in wall.windows:
                    output += window.area * window.glass['TOT-SOL-TRANS']
        return output * self.electricEquivalentEfficiencyHeat
    
    def calculateHeatSSEff(self, listOfProps):      # originalValues is dictionary and listOfProps is a list of class Prop objects
        # Set up desired values
        currentHeatGenSeff = self['HEAT-GEN-SEFF']
        oldHeatSseff = self['HEAT-SSEFF']
        
        newHeatGenSeff = None
        for prop in listOfProps:
            if prop.key == 'HEAT-GEN-SEFF':
                newHeatGenSeff = prop.value
        
        return oldHeatSseff * newHeatGenSeff / oldHeatSseff
    
    @property 
    def areaWeightedInternalConduction(self): 
        output = 0
        for zone in self.zones.objects:
            for wall in zone.walls.objects:
                if wall['TYPE'] == 'Unheated adjoining space':
                    output += wall.area * wall.construction['U-VALUE']
        return output * self.electricEquivalentEfficiencyHeat 
      
    # When heating heat - external_temp will always be positive
    """@property 
    def areaAndHeatSetPointWeightedInternalConduction(self): 
        output = 0
        for zone in self.zones.objects:
            for wall in zone.walls.objects:
                if wall['TYPE'] == 'Unheated adjoining space':
                    output += wall.area * wall.construction['U-VALUE'] * max([0.0, (zone.activity.heat_set_point - external_temp)])
        return output * self.electricEquivalentEfficiencyHeat 
    
    # When cooling cool - external_temp will always be negative
    @property 
    def areaAndCoolSetPointWeightedInternalConduction(self): 
        output = 0
        for zone in self.zones.objects:
            for wall in zone.walls.objects:
                if wall['TYPE'] == 'Unheated adjoining space':
                    output += wall.area * wall.construction['U-VALUE'] * min([0.0, (zone.activity.cool_set_point - external_temp)])
        return output * self.electricEquivalentEfficiencyHeat 
    """
    
    