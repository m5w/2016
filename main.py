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

class BacteriumDeath: # to-do: derive this from object
    pass

class BacteriumBinaryFission(BaseException):
    def __init__(self, bacterium):
        self._bacterium = bacterium

    def bacterium(self):
        return self._bacterium

class Bacterium(object):
    def __init__(self, BINARY_FISSION_BIOMASS, DEATH_PROBABILITY, growth_rate, substrate_consumption_rate, biomass):
        self._BINARY_FISSION_BIOMASS = BINARY_FISSION_BIOMASS
        self._DEATH_PROBABILITY = DEATH_PROBABILITY
        self._growth_rate = growth_rate
        self._substrate_consumption_rate = substrate_consumption_rate
        self._biomass = biomass

    def biomass(self):
        return self._biomass

    def substrate_consumption_rate(self, substrate_concentration):
        if self._biomass >= self._BINARY_FISSION_BIOMASS:
            biomass = self._biomass
            self._biomass /= 2.0
            raise BacteriumBinaryFission(Bacterium(self._BINARY_FISSION_BIOMASS, self._DEATH_PROBABILITY, self._growth_rate, self.substrate_consumption_rate, biomass - self._biomass))

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

        bacterium = 0
        while True:
            try:
                self._substrate_concentration -= self._bacteria[bacterium].substrate_consumption_rate(substrate_concentration)
                bacteria.append(self._bacteria[bacterium])
            # to-do: research if the try block can be executed from an except block
            # obsolete: just add the bacteria to the end
            except BacteriumBinaryFission as bacterium_binary_fission:
                print 'binary fission'
                print 'len was', len(self._bacteria)
                self._bacteria.append(self._bacteria[bacterium])
                self._bacteria.append(bacterium_binary_fission.bacterium())
                print 'len is', len(self._bacteria)
            except(BacteriumDeath): # to-do: remove parentheses
                pass
            except IndexError:
                break

            print 'iadd'
            print 'bacterium was', bacterium
            bacterium += 1
            print 'bacterium is', bacterium

        self._bacteria = bacteria
