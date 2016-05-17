import numpy
import random
import scipy.stats

def get_specific_growth_rate_monod(MAXIMUM_SPECIFIC_GROWTH_RATE, SUBSTRATE_SATURATION_CONSTANT):
    def specific_growth_rate_monod(SUBSTRATE_CONCENTRATION):
        return MAXIMUM_SPECIFIC_GROWTH_RATE * SUBSTRATE_CONCENTRATION / (SUBSTRATE_SATURATION_CONSTANT + SUBSTRATE_CONCENTRATION)

    return specific_growth_rate_monod

def get_bacterium_monod(monod):
    def bacterium_monod(SUBSTRATE_CONCENTRATION, BACTERIUM):
        return monod(SUBSTRATE_CONCENTRATION, BACTERIUM.biomass())

    return bacterium_monod

def get_growth_rate_monod(specific_growth_rate_monod):
    @get_bacterium_monod
    def growth_rate_monod(SUBSTRATE_CONCENTRATION, BIOMASS):
        return specific_growth_rate_monod(SUBSTRATE_CONCENTRATION) * BIOMASS

    return growth_rate_monod

def get_substrate_consumption_rate_monod(YIELD_COEFFICIENT, specific_growth_rate_monod):
    YIELD_COEFFICIENT_INVERSE = 1.0 / YIELD_COEFFICIENT

    @get_bacterium_monod
    def substrate_consumption_rate_monod(SUBSTRATE_CONCENTRATION, biomass):
        return YIELD_COEFFICIENT_INVERSE * specific_growth_rate_monod(SUBSTRATE_CONCENTRATION) * biomass

    return substrate_consumption_rate_monod

class BacteriumDeath(BaseException):
    pass

class BacteriumBinaryFission(BaseException):
    def __init__(self, BACTERIUM):
        self._BACTERIUM = BACTERIUM

    def bacterium(self):
        return self._BACTERIUM

class Bacterium(object):
    def __init__(self, SPECIES, BINARY_FISSION_BIOMASS, DEATH_PROBABILITY, growth_rate, substrate_consumption_rate, BIOMASS):
        self._SPECIES = SPECIES
        self._BINARY_FISSION_BIOMASS = BINARY_FISSION_BIOMASS
        self._DEATH_PROBABILITY = DEATH_PROBABILITY
        self._growth_rate = growth_rate
        self._substrate_consumption_rate = substrate_consumption_rate
        self._biomass = BIOMASS

    def get_species(self):
        return self._SPECIES

    def get_biomass(self):
        return self._biomass

    def get_substrate_consumption_rate(self, SUBSTRATE_CONCENTRATION):
        if self._biomass >= self._BINARY_FISSION_BIOMASS:
            BIOMASS = self._biomass
            self._biomass /= 2.0
            raise BacteriumBinaryFission(Bacterium(self._BINARY_FISSION_BIOMASS, self._DEATH_PROBABILITY, self._growth_rate, self._substrate_consumption_rate, BIOMASS - self._biomass))

        # Since random.random() ``-> x in the interval [0, 1)" (Python 2.7 online help utility), random.random() will never be less than zero but always less than 1.
        if random.random() < self._DEATH_PROBABILITY:
            raise BacteriumDeath

        SUBSTRATE_CONSUMPTION_RATE = self._substrate_consumption_rate(SUBSTRATE_CONCENTRATION, self)
        self._biomass += self._growth_rate(SUBSTRATE_CONCENTRATION, self)
        return SUBSTRATE_CONSUMPTION_RATE

class Chemostat(object):
    def __init__(self, SUBSTRATE_CONCENTRATION, VOLUME):
        self._substrate_concentration = SUBSTRATE_CONCENTRATION
        self._volume = VOLUME

        self._bacteria = []

        self._substrate_mass = self._substrate_concentration * self._volume

    def extend_bacteria(self, L):
        self._bacteria.extend(L)

    def _get_substrate_concentration(self, INFLOW_SUBSTRATE_CONCENTRATION, INFLOW_VOLUME, OUTFLOW_VOLUME):
        self._substrate_mass += INFLOW_SUBSTRATE_CONCENTRATION * INFLOW_VOLUME - self._substrate_concentration * OUTFLOW_VOLUME
        self._volume += INFLOW_VOLUME - OUTFLOW_VOLUME
        self._substrate_concentration = self._substrate_mass / self._volume
        return self._substrate_concentration

    def substrate_concentration(self, INFLOW_SUBSTRATE_CONCENTRATION, INFLOW_VOLUME, OUTFLOW_VOLUME):
        SUBSTRATE_CONCENTRATION = self._get_substrate_concentration(INFLOW_SUBSTRATE_CONCENTRATION, INFLOW_VOLUME, OUTFLOW_VOLUME)

        bacteria = []

        bacterium = 0

        while True:
            try:
                self._substrate_concentration -= self._bacteria[bacterium].substrate_consumption_rate(SUBSTRATE_CONCENTRATION)
                bacteria.append(self._bacteria[bacterium])
            except BacteriumBinaryFission as bacterium_binary_fission:
                self._bacteria.append(self._bacteria[bacterium])
                self._bacteria.append(bacterium_binary_fission.bacterium())
            except BacteriumDeath:
                pass
            except IndexError:
                break

            bacterium += 1

        self._bacteria = bacteria
