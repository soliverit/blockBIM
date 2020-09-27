from .sbem_object import SbemObject
from .sbem_zone import SbemZone
from decimal import Decimal

class SbemDhwGenerator(SbemObject):
    """ Conversion constant
    Q_dot = m_dot * c * deltaT
    
    m_dot = density * demand in kg / second
    where:
        density = 1000 kg/m3
        demand = demand per person per day * number of persons per m2 * area (the former two come from the activity spreadsheet and the latter comes from the zones it affects - needs to be in m3 / second)
    
    c = 4.186 kJ/kg-K (specific heat capacity of water)
    deltaT = (273.15 + 55) - (273.15 + 10) = 45 Kelvin
    """
    DEMAND_FACTOR = Decimal('0.002180208')
    
    def __init__(self, sbemModel, json):
        super(self.__class__,self).__init__(sbemModel,json)
    
    @property
    def efficiency(self):
    ##### ADD ELEC EQUIV EFF #####
        return self["DHW-GEN-SEFF"] if "DHW-GEN-SEFF" in self else self["HVAC-SYSTEM-EFF"]
    
    @property
    def area(self):
        #return self.sbemModel.objects.filterByClassAndProperty(SbemZone,"DHW-GENERATOR", self.name).sum("area")
        return self.relatedZones.sum("area")
    
    @property
    def relatedZones(self):
        return self.sbemModel.classifiedObjects[SbemZone].filterByProperty("DHW-GENERATOR", self.name)

