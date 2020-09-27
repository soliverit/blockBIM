###### SBEM OBJECT SET GROUP ######
#
# Err, a set for storing sets...
#
# Chainable group manipulations for querying object sets
class SbemObjectSetGroup():
    #SEE COMMENT ON ABUSING sbem_object.py in sbem_object_set.py as base class for subscription
    def __getitem__(self, key):
        if key not in self:
            return self.defaultClass()
        return self.sets[key]
    #Create empty self(), need to supply what the default output class is because if we try and specify SbemObjectSet explicity we get a circular reference
    def __init__(self, key, defaultClass):
        self.key = key
        self.sets = dict()
        self.defaultClass = defaultClass
    #SEE COMMENT ON ABUSING.... for subscript
    def __setitem__(self, key, sbemObjectSet):
        if key not in self.sets:
            self.sets[key] = sbemObjectSet
    #Set is present with the group
    def __contains__(self, key):
        return key in list(self.sets)
    #Number of sets in the group
    def __len__(self):
        return len(self.sets)
    #Iterate over all sets and regroup objects based on their keyed value
    def reGroupBy(self, key):
        output = self.__class__(key, self.defaultClass)
        for k in self.sets.keys():
            for obj in self.sets[k].objects:
                if obj[key] not in output:
                    output[obj[key]] = self.defaultClass()
                output[obj[key]].append(obj)
        return output
    #Take an SbemObjectSet and merge it with the current sets
    def mergeSbemObjectSet(self, set):
        groupSet = set.groupBy(self.key)
        for key, sset in groupSet.sets.items():
            if not self[key]:
                self[key] = self.defaultClass()
            for obj in sset.objects:
                self[key].append(obj)
        return self
    #General print`
    def print(self):
        for k, v in self.sets.items():
            print(str(k) + "\t " + str(len(v)))


