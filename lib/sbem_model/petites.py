
import numpy as np
import pandas as pd
from decimal import Decimal
import re

# Regex for preventing lots of trailing characters
REGEX = re.compile('[0-9]+\.[0-9]*([0]{6,}|[9]{6,})')
REGEX_FLOAT = re.compile('\d+\.\d+')
REGEX_TRAILING = re.compile('([0]+)$')

def readCSV(file_path, column_to_filter, value_to_filter):
    csv_data = pd.read_csv(file_path, header = 0)
    
    csv_data = csv_data[csv_data[column_to_filter] == value_to_filter]
    
    return_dict = csv_data.to_dict(orient = 'records')[0]
    
    for k, v in return_dict.items():
        if type(v) in [int, float]:
            return_dict[k] = Decimal(str(v))
    
    return DotDict(return_dict)

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    def __getattr__(self, attr):
        return self.get(attr)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self

def convertToSnakeCase(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# Convert a number (usually a decimal or string) to a sensible rounding error
def automagicallyRound(val):
    # Attempts to fix the rounding issue
    # Convert to string
    if type(val) != str:
        val_str = str(val)
    else:
        val_str = val
    
    # Try and match
    m = REGEX.match(val_str)
    if m:
        m_dec = Decimal(m[0])
        numDecPlaces = m_dec.as_tuple().exponent
        m_rounded = round(m_dec, abs(numDecPlaces) - 1)
        val_str = str(m_rounded)
    
    # Only removing trailing zeroes if there are numbers after the decimal point (to prevent truncating 1000 etc)
    if REGEX_FLOAT.match(val_str):
        val_str = str(REGEX_TRAILING.sub('', val_str))
    
    return val_str
    

# A group by which won't remove rows when the grouped columns have NaN values in them
def safeGroupBy(df, group_cols, agg_dict):
    # set name of group col to unique value
    group_id = 'group_id'
    while group_id in df.columns:
        group_id += 'x'
    # get final order of columns
    agg_col_order = (group_cols + list(agg_dict.keys()))
    # create unique index of grouped values
    group_idx = df[group_cols].drop_duplicates()
    group_idx[group_id] = np.arange(group_idx.shape[0])
    # merge unique index on dataframe
    df = df.merge(group_idx, on=group_cols)
    # group dataframe on group id and aggregate values
    df_agg = df.groupby(group_id, as_index=True).agg(agg_dict)
    # merge grouped value index to results of aggregation
    df_agg = group_idx.set_index(group_id).join(df_agg)
    # rename index
    df_agg.index.name = None
    # return reordered columns
    return df_agg[agg_col_order]
    

# Import a class dynamically based on its name
def importClassByName(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


    