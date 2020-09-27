from .sbem_object import SbemObject
from .sbem_object_set import SbemObjectSet
from .sbem_wall import SbemWall
from .petites import readCSV

from decimal import Decimal

class SbemZone(SbemObject):
    ACTIVITY_CACHE = {}
    LAMP_EFFICACY = {
        'LED': 50,
        'Tungsten or Halogen': 9,
        'Fluorescent - compact': 27,
        'T12 Fluorescent - halophosphate - low frequency ballast': 30,
        'T8 Fluorescent - halophosphate - low frequency ballast': 33,
        'T8 Fluorescent - halophosphate - high frequency ballast': 39,
        'T8 Fluorescent - triphosphor - high frequency ballast': 43.5,
        'Metal Halide': 39,
        'High Pressure Mercury': 27,
        'High Pressure Sodium': 42,
        'T5 Fluorescent - triphosphor-coated - high frequency ballast': 45,
        'Fluorescent (no details)': 27,
        None: 9}
    OCC_SENSOR_FACTORS = {
        'NONE': 1,
        'MAN-ON-AUTO-OFF': 0.82,
        'AUTO-ON-OFF': 0.9,
        'AUTO-ON-DIMMED': 0.95,
        'MAN-ON-OFF+EXT': 0.95,
        'MAN-ON-DIMMED': 0.9}
    CHOSEN = 'CHOSEN'
    WORK_PLANE_HEIGHT = Decimal('0.75')
    DECIMAL_ZERO = Decimal('0')
    
    def __init__(self, sbemModel, json):
        super(self.__class__,self).__init__(sbemModel, json)
        if "Q50-INF" not in self:
            self["Q50-INF"] = 10
        self.walls = SbemObjectSet()
        self.sbem_activity_type = False
        self.dhw_generator = False
        for wall in json["walls"]:
            self.walls.append(SbemWall(sbemModel, wall))
    
    def __str__(self):
        string = super().__str__()
        for wall in self.walls.objects:
            string += str(wall)
        return string
    
    @property
    def dhw(self):
        if self.dhw_generator is False:
            self.dhw_generator = self.sbemModel.findObject(self["DHW-GENERATOR"])
        return self.dhw_generator
    
    @property
    def activity(self):
        if not self.sbem_activity_type:
            strActivityID = str(self["ACTIVITY"])
            if strActivityID not in self.__class__.ACTIVITY_CACHE:
                #self.sbem_activity_type = SbemActivityType.find_by([['sbem_activity_id', self['ACTIVITY']]])
                self.sbem_activity_type = readCSV(file_path = 'data/db/sbem_activity_types.csv', column_to_filter = 'sbem_activity_id', value_to_filter = self['ACTIVITY'])
                self.__class__.ACTIVITY_CACHE[strActivityID] = self.sbem_activity_type
            else:
                self.sbem_activity_type = self.__class__.ACTIVITY_CACHE[strActivityID]
        return self.sbem_activity_type
    
    @property
    def internalGains(self):
        return (self.activity.metabolic_rate * self.activity.occupancy + self.activity.equipment_gains)
    
    @property
    def airFlowRate(self):
        return self.activity.occupancy * self.activity.fresh_air_rate * self.area
    
    @property
    def areaWeightedHotWaterDemand(self):
        return self.activity.hot_water_demand * self.area
    
    @property
    def lpd(self):
        pd = False
        if self['LIGHT-CASE'] == 'UNKNOWN':
            eff = Decimal(__class__.LAMP_EFFICACY[self['LIGHT-TYPE']])
        elif self['LIGHT-CASE'] == 'CHOSEN':
            eff = Decimal(self['LAMP-BALLAST-EFF']) * Decimal(self['LIGHT-OUTPUT-RATIO'])
        else:
            pd = self['LIGHT-ACT-WATT'] / self.area
        if not pd:
            if self.roomHeight < self.WORK_PLANE_HEIGHT:
                pd = self.DECIMAL_ZERO
            else:
                pd = self.activity['light_lux'] * (self.roomHeight - self.WORK_PLANE_HEIGHT)**2 / (eff * self.area)
        return pd * self.OCC_SENSOR_FACTORS[self["OCC-SENS-T"]] if self["OCC-SENS-T"] else pd
      
    # Calculate the number of lamps in the zone, requires the nominal wattage from the unit costs sheet
    def numLamps(self, nominalWattage):
        numLamps = self.lpd * self.AREA / nominalWattage
        return numLamps
    
    @property
    def roomHeight(self):
        return self['HEIGHT']
    
    @property
    def wallSurfaces(self):
        return self.walls.groupBy("ORIENTATION")    
    
    @property
    def occsensor(self):
        value = self.OCC_SENSOR_FACTORS[self["LIGHT-OCC-SENS-T"]] if "LIGHT-CC-SENS-T" in self else None
        if not value:
            value = 1
        return value
    
    def upgradeToNextGreaterEfficacyTemplate(self):
        if self["LIGHT-TYPE"] == "LED":
            return False
        temp = self.LAMP_EFFICACY[self["LIGHT-TYPE"]]
        dist = 999
        outKey = False    
        for k, v in self.LAMP_EFFICACY.items():
            if v > temp and (v - temp )< dist:
                dist = v - temp
                outKey = k
        self["LIGHT-TYPE"] = outKey
        return True
    
    def toChosen(self):
        if self["LIGHT-CASE"] != self.CHOSEN:
            self["LIGHT-CASE"] = self.CHOSEN
            self["LAMP-BALLAST-EFF"] = self.LAMP_EFFICACY[self["LIGHT-TYPE"]]
            self["LIGHT-OUTPUT-RATIO"] = 1
            self.originalProps["LAMP-BALLAST-EFF"] = self.LAMP_EFFICACY[self["LIGHT-TYPE"]]
            self.originalProps["LIGHT-OUTPUT-RATIO"] = 1
