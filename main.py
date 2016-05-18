import random
import scipy.stats

def get_specific_growth_rate_monod(MAXIMUM_SPECIFIC_GROWTH_RATE, SUBSTRATE_SATURATION_CONSTANT):
    def specific_growth_rate_monod(SUBSTRATE_CONCENTRATION):
        return MAXIMUM_SPECIFIC_GROWTH_RATE * SUBSTRATE_CONCENTRATION / (SUBSTRATE_SATURATION_CONSTANT + SUBSTRATE_CONCENTRATION)

    return specific_growth_rate_monod

def get_bacterium_monod(monod):
    def bacterium_monod(SUBSTRATE_CONCENTRATION, BACTERIUM):
        return monod(SUBSTRATE_CONCENTRATION, BACTERIUM.get_biomass())

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

class Species(object):
    def __init__(self, BINARY_FISSION_BIOMASS, DEATH_PROBABILITY, growth_rate, substrate_consumption_rate, BIOMASS):
        self._BINARY_FISSION_BIOMASS = BINARY_FISSION_BIOMASS
        self._DEATH_PROBABILITY = DEATH_PROBABILITY
        self._growth_rate = growth_rate
        self._substrate_consumption_rate = substrate_consumption_rate
        self._BIOMASS = BIOMASS

    def get_binary_fission_biomass(self):
        return self._BINARY_FISSION_BIOMASS

    def get_death_probability(self):
        return self._DEATH_PROBABILITY

    def get_growth_rate(self):
        return self._growth_rate

    def get_substrate_consumption_rate(self):
        return self._substrate_consumption_rate

    def get_biomass(self):
        return self._BIOMASS

class Bacterium(object):
    def __init__(self, SPECIES):
        self._SPECIES = SPECIES

        self._biomass = self._SPECIES.get_biomass()

    def get_species(self):
        return self._SPECIES

    def get_biomass(self):
        return self._biomass

    def get_substrate_consumption_rate(self, SUBSTRATE_CONCENTRATION):
        if self._biomass >= self._SPECIES.get_binary_fission_biomass():
            self._biomass /= 2.0
            raise BacteriumBinaryFission(Bacterium(self._SPECIES))

        # Since random.random() ``-> x in the interval [0, 1)" (Python 2.7 online help utility), random.random() will never be less than zero but always less than 1.
        if random.random() < self._SPECIES.get_death_probability():
            raise BacteriumDeath

        SUBSTRATE_CONSUMPTION_RATE = self._SPECIES.get_substrate_consumption_rate()(SUBSTRATE_CONCENTRATION, self)
        self._biomass += self._SPECIES.get_growth_rate()(SUBSTRATE_CONCENTRATION, self)
        return SUBSTRATE_CONSUMPTION_RATE

class Chemostat(object):
    def __init__(self, SUBSTRATE_CONCENTRATION, VOLUME):
        self._substrate_concentration = SUBSTRATE_CONCENTRATION
        self._volume = VOLUME

        self._bacteria = []
        self._bacteria_population = {}

        self._substrate_mass = self._substrate_concentration * self._volume

    def iadd_bacteria(self, SPECIES, LEN_):
        self._bacteria += [Bacterium(SPECIES) for bacterium in xrange(LEN_)]

        try:
            self._bacteria_population[SPECIES] += LEN_
        except KeyError:
            self._bacteria_population[SPECIES] = LEN_

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
                self._substrate_concentration -= self._bacteria[bacterium].get_substrate_consumption_rate(SUBSTRATE_CONCENTRATION)
                bacteria.append(self._bacteria[bacterium])
            except BacteriumBinaryFission as bacterium_binary_fission:
                self._bacteria.append(self._bacteria[bacterium])
                self._bacteria.append(bacterium_binary_fission.bacterium())
                self._bacteria_population[self._bacteria[bacterium].get_species()] += 1
            except BacteriumDeath:
                self._bacteria_population[self._bacteria[bacterium].get_species()] -= 1
            except IndexError:
                break

            bacterium += 1

        self._bacteria = bacteria

class Step(object):
    def __init__(self):
        raise NotImplementedError

    def get_period(self):
        raise NotImplementedError

    def get_inflow_concentration(self):
        raise NotImplementedError

    def get_inflow_volume(self):
        raise NotImplementedError

    def get_outflow_volume(self):
        raise NotImplementedError

    def get_species(self):
        raise NotImplementedError

    def get_len_(self):
        raise NotImplementedError
