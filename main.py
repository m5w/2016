import numpy
import random
import scipy.stats

def get_specific_growth_rate_monod(MAXIMUM_SPECIFIC_GROWTH_RATE, SUBSTRATE_SATURATION_CONSTANT):
    def specific_growth_rate_monod(substrate_concentration):
        return MAXIMUM_SPECIFIC_GROWTH_RATE * substrate_concentration / (SUBSTRATE_SATURATION_CONSTANT + substrate_concentration)

    return specific_growth_rate_monod

def get_bacterium_monod(monod):
    def bacterium_monod(substrate_concentration, bacterium):
        return monod(substrate_concentration, bacterium.biomass())

    return bacterium_monod

def get_growth_rate_monod(specific_growth_rate_monod):
    @get_bacterium_monod
    def growth_rate_monod(substrate_concentration, biomass):
        return specific_growth_rate_monod(substrate_concentration) * biomass

    return growth_rate_monod

def get_substrate_consumption_rate_monod(YIELD_COEFFICIENT, specific_growth_rate_monod):
    assert type(YIELD_COEFFICIENT) is float
    YIELD_COEFFICIENT_INVERSE = 1.0 / YIELD_COEFFICIENT

    @get_bacterium_monod
    def substrate_consumption_rate_monod(substrate_concentration, biomass):
        return YIELD_COEFFICIENT_INVERSE * specific_growth_rate_monod(substrate_concentration) * biomass

    return substrate_consumption_rate_monod

class BacteriumDeath:
    pass

class Bacterium(object):
    def __init__(self, DEATH_PROBABILITY, growth_rate, substrate_consumption_rate, biomass):
        self._DEATH_PROBABILITY = DEATH_PROBABILITY
        self._growth_rate = growth_rate
        self._substrate_consumption_rate = substrate_consumption_rate
        self._biomass = biomass

    def biomass(self):
        return self._biomass

    def substrate_consumption_rate(self, substrate_concentration):
        # Since random.random() ``-> x in the interval [0, 1)" (Python 2.7 online help utility), random.random() will never be less than zero but always less than 1.
        if random.random() < self._DEATH_PROBABILITY:
            raise BacteriumDeath

        substrate_consumption_rate_ = self._substrate_consumption_rate(substrate_concentration, self)
        self._biomass += self._growth_rate(substrate_concentration, self)
        return substrate_consumption_rate_

class Chemostat(object):
    def __init__(self, substrate_concentration):
        self._substrate_concentration = substrate_concentration

        self._bacteria = []

    def get_substrate_concentration(self):
        substrate_concentration = self._substrate_concentration
        bacteria = []

        for bacterium in self._bacteria:
            try:
                self._substrate_concentration -= bacterium.substrate_consumption_rate(substrate_concentration)
                bacteria.append(bacterium)
            except(BacteriumDeath):
                pass

        self._bacteria = bacteria
