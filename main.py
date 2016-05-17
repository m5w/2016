import numpy
import random
import scipy.stats

def accumulate(L, init = 0, op = lambda a, b: a + b):
    for b in L:
        init = op(init, b)

    return init

def get_specific_growth_rate_monod(MAXIMUM_SPECIFIC_GROWTH_RATE, SUBSTRATE_SATURATION_CONSTANT):
    def specific_growth_rate_monod(substrate_concentration):
        return MAXIMUM_SPECIFIC_GROWTH_RATE * substrate_concentration / (SUBSTRATE_SATURATION_CONSTANT + substrate_concentration)

    return specific_growth_rate_monod

def get_growth_rate_monod(specific_growth_rate_monod):
    def growth_rate_monod(substrate_concentration, biomass):
        return specific_growth_rate_monod(substrate_concentration) * biomass

    return growth_rate_monod

def get_substrate_consumption_rate_monod(YIELD_COEFFICIENT, specific_growth_rate_monod):
    assert type(YIELD_COEFFICIENT) is float
    YIELD_COEFFICIENT_INVERSE = 1.0 / YIELD_COEFFICIENT

    def substrate_consumption_rate_monod(substrate_concentration, biomass):
        return YIELD_COEFFICIENT_INVERSE * specific_growth_rate_monod(substrate_concentration) * biomass

    return substrate_consumption_rate_monod

class Bacterium(object):
    def __init__(self, specific_growth_rate, biomass):
        self._specific_growth_rate = specific_growth_rate
        self._biomass = biomass
