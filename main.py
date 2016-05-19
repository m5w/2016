from ps8 import setFigure as figure, join

import random
import string

import numpy
import pylab

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

class BacteriumSpecies(object):
    def __init__(self, STR_, BINARY_FISSION_BIOMASS, DEATH_PROBABILITY, growth_rate, substrate_consumption_rate):
        self._STR_ = STR_
        self._BINARY_FISSION_BIOMASS = BINARY_FISSION_BIOMASS
        self._DEATH_PROBABILITY = DEATH_PROBABILITY
        self._growth_rate = growth_rate
        self._substrate_consumption_rate = substrate_consumption_rate

        self._BIOMASS = self._BINARY_FISSION_BIOMASS / 2.0

    def __str__(self):
        return self._STR_

    def get_binary_fission_biomass(self):
        return self._BINARY_FISSION_BIOMASS

    def get_death_probability(self):
        return self._DEATH_PROBABILITY

    def get_growth_rate(self):
        return self._growth_rate

    def get_substrate_consumption_rate(self):
        return self._substrate_consumption_rate

    def get_biomass(self):
        return random.uniform(self._BIOMASS, self._BINARY_FISSION_BIOMASS)

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
        self._species_bacterium_frequency = {}

    def add_bacteria(self, SPECIES, BACTERIUM_FREQUENCY):
        self._bacteria += [Bacterium(SPECIES) for bacterium in xrange(BACTERIUM_FREQUENCY)]

        try:
            self._species_bacterium_frequency[SPECIES] += BACTERIUM_FREQUENCY
        except KeyError:
            self._species_bacterium_frequency[SPECIES] = BACTERIUM_FREQUENCY

    def _get_substrate_concentration(self, INFLOW_SUBSTRATE_CONCENTRATION, INFLOW_VOLUME, OUTFLOW_VOLUME):
        self._substrate_mass = self._substrate_concentration * self._volume
        self._substrate_mass += INFLOW_SUBSTRATE_CONCENTRATION * INFLOW_VOLUME - self._substrate_concentration * OUTFLOW_VOLUME
        self._volume += INFLOW_VOLUME - OUTFLOW_VOLUME
        self._substrate_concentration = self._substrate_mass / self._volume
        return self._substrate_concentration

    def get_substrate_concentration(self, INFLOW_SUBSTRATE_CONCENTRATION, INFLOW_VOLUME, OUTFLOW_VOLUME):
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
                self._species_bacterium_frequency[self._bacteria[bacterium].get_species()] += 1
            except BacteriumDeath:
                self._species_bacterium_frequency[self._bacteria[bacterium].get_species()] -= 1
            except IndexError:
                break

            bacterium += 1

        self._substrate_concentration = max(self._substrate_concentration, 0)

        self._bacteria = bacteria

        return self._substrate_concentration

    def get_species_bacterium_frequency(self, BACTERIUM_SPECIES):
        return self._species_bacterium_frequency[BACTERIUM_SPECIES]

class Observer(object):
    def __init__(self):
        raise NotImplementedError

    def observe_time(self, chemostat, TIME, INFLOW_SUBSTRATE_CONCENTRATION, INFLOW_VOLUME, OUTFLOW_VOLUME):
        raise NotImplementedError

    def observe_trial(self, chemostat):
        raise NotImplementedError

    """ initial_bacterium_frequency is a dict of bacteria species to frequencies. """
    def graph(self, SUBTITLE, TRIAL_FREQUENCY, INITIAL_SUBSTRATE_CONCENTRATION, SPECIES_INITIAL_BACTERIUM_FREQUENCY, TIME_FREQUENCY):
        raise NotImplementedError

def get_trial_time_frequency(time_frequency):
    return [[] for trial in xrange(time_frequency)]

class TimeMeanBacteriumSpeciesFrequencyObserver(Observer):
    """ BACTERIUM_SPECIES is a list. """
    def __init__(self, TIME_FREQUENCY, BACTERIUM_SPECIES):
        self._trial_time_substrate_concentration = get_trial_time_frequency(TIME_FREQUENCY)
        self._trial_time_species_bacterium_frequency = {}

        for BACTERIUM_SPECIES_ in BACTERIUM_SPECIES:
            self._trial_time_species_bacterium_frequency[BACTERIUM_SPECIES_] = get_trial_time_frequency(TIME_FREQUENCY)

    def observe_time(self, chemostat, TIME, INFLOW_SUBSTRATE_CONCENTRATION, INFLOW_VOLUME, OUTFLOW_VOLUME):
        self._trial_time_substrate_concentration[TIME].append(chemostat.get_substrate_concentration(INFLOW_SUBSTRATE_CONCENTRATION, INFLOW_VOLUME, OUTFLOW_VOLUME))

        for BACTERIUM_SPECIES_ in self._trial_time_species_bacterium_frequency:
            self._trial_time_species_bacterium_frequency[BACTERIUM_SPECIES_][TIME].append(chemostat.get_species_bacterium_frequency(BACTERIUM_SPECIES_))

    def observe_trial(self, chemostat):
        pass

    """ initial_bacterium_frequency is a dict of bacteria species to frequencies. """
    def graph(self, SUBTITLE, TRIAL_FREQUENCY, INITIAL_SUBSTRATE_CONCENTRATION, TIME_FREQUENCY):
        x = xrange(TIME_FREQUENCY)
        time_mean_substrate_concentration = []

        for TRIAL_SUBSTRATE_CONCENTRATION in self._trial_time_substrate_concentration:
            time_mean_substrate_concentration.append(numpy.mean(TRIAL_SUBSTRATE_CONCENTRATION))

        time_species_mean_bacterium_frequency = {}

        for BACTERIUM_SPECIES_ in self._trial_time_species_bacterium_frequency:
            iterator = self._trial_time_species_bacterium_frequency[BACTERIUM_SPECIES_].__iter__()
            trial_species_bacterium_frequency = next(iterator)
            time_species_mean_bacterium_frequency[BACTERIUM_SPECIES_] = [numpy.mean(trial_species_bacterium_frequency)]

            while True:
                try:
                    trial_species_bacterium_frequency = next(iterator)
                except StopIteration:
                    break

                time_species_mean_bacterium_frequency[BACTERIUM_SPECIES_].append(numpy.mean(trial_species_bacterium_frequency))

        figure()
        pylab.plot(x, time_mean_substrate_concentration)
        XLABEL_ = 'Time'
        YLABEL_ = str(TRIAL_FREQUENCY) + '-Trial Mean Substrate Concentration'
        pylab.title(YLABEL_ + ' v. ' + XLABEL_ + SUBTITLE)
        pylab.xlabel(XLABEL_)
        pylab.ylabel(YLABEL_)

        figure()

        for BACTERIUM_SPECIES_ in time_species_mean_bacterium_frequency:
            pylab.plot(x, time_species_mean_bacterium_frequency[BACTERIUM_SPECIES_])
            XLABEL_ = 'Time'
            YLABEL_ = str(TRIAL_FREQUENCY) + '-Trial Mean ' + str(BACTERIUM_SPECIES_) + ' Population'
            pylab.title(YLABEL_ + ' v. ' + XLABEL_ + SUBTITLE)
            pylab.xlabel(XLABEL_)
            pylab.ylabel(YLABEL_)

class Step(object):
    def __init__(self):
        raise NotImplementedError

    def get_period(self):
        raise NotImplementedError

    def get_inflow_substrate_concentration(self):
        raise NotImplementedError

    def get_inflow_volume(self):
        raise NotImplementedError

    def get_outflow_volume(self):
        raise NotImplementedError

    def get_bacterium_species(self):
        raise NotImplementedError

    def get_bacterium_frequency(self):
        raise NotImplementedError

    def do(self, t_0, observer, chemostat):
        raise NotImplementedError

class PeriodStep(Step):
    def __init__(self, PERIOD, INFLOW_SUBSTRATE_CONCENTRATION, INFLOW_VOLUME, OUTFLOW_VOLUME):
        self._PERIOD = PERIOD
        self._INFLOW_SUBSTRATE_CONCENTRATION = INFLOW_SUBSTRATE_CONCENTRATION
        self._INFLOW_VOLUME = INFLOW_VOLUME
        self._OUTFLOW_VOLUME = OUTFLOW_VOLUME

    def get_period(self):
        return self._PERIOD

    def get_inflow_substrate_concentration(self):
        return self._INFLOW_SUBSTRATE_CONCENTRATION

    def get_inflow_volume(self):
        return self._INFLOW_VOLUME

    def get_outflow_volume(self):
        return self._OUTFLOW_VOLUME

    def do(self, initial_time, observer, chemostat):
        for TIME in xrange(initial_time, initial_time + self._PERIOD):
            observer.observe_time(chemostat, TIME, self._INFLOW_SUBSTRATE_CONCENTRATION, self._INFLOW_VOLUME, self._OUTFLOW_VOLUME)

class BacteriaStep(Step):
    def __init__(self, BACTERIUM_SPECIES, BACTERIUM_FREQUENCY):
        self._BACTERIUM_SPECIES = BACTERIUM_SPECIES
        self._BACTERIUM_FREQUENCY = BACTERIUM_FREQUENCY

    def get_bacterium_species(self):
        return self._BACTERIUM_SPECIES

    def get_bacterium_frequency(self):
        return self._BACTERIUM_FREQUENCY

    def do(self, initial_time, observer, chemostat):
        chemostat.add_bacteria(self._BACTERIUM_SPECIES, self._BACTERIUM_FREQUENCY)

def accumulate(L, init = 0, op = lambda a, b: a + b):
    for b in L:
        init = op(init, b)

    return init

class Procedure(object):
    def __init__(self, STEPS, TRIAL_FREQUENCY, OBSERVER_TYPE):
        self._STEPS = STEPS
        self._TRIAL_FREQUENCY = TRIAL_FREQUENCY
        self._OBSERVER_TYPE = OBSERVER_TYPE

        self._bacteria_species = []

        subtitle = []
        time = 0

        bacteria = []

        iterator = self._STEPS.__iter__()

        while True:
            try:
                step = next(iterator)
            except StopIteration:
                break

            try:
                time += step.get_period()
            except NotImplementedError:
                pass

            try:
                self._add_bacteria(bacteria, step)
            except NotImplementedError:
                continue

            try:
                while True:
                    step = next(iterator)

                    try:
                        self._add_bacteria(bacteria, step)
                    except NotImplementedError:
                        break
            except StopIteration:
                self._add_subtitle(subtitle, bacteria, time)
                break

            self._add_subtitle(subtitle, bacteria, time)

            bacteria = []

            time += step.get_period()

        self._subtitle = '\n' + join(subtitle, ';') + '.'
        self._TIME_FREQUENCY = time

    @classmethod
    def _add_subtitle(cls, subtitle, BACTERIA, TIME):
        subtitle.append(join([str(BACTERIUM_FREQUENCY) + ' ' + str(BACTERIUM_SPECIES) for BACTERIUM_SPECIES, BACTERIUM_FREQUENCY in BACTERIA]) + ' ')

        if accumulate([BACTERIUM_FREQUENCY for BACTERIUM_SPECIES, BACTERIUM_FREQUENCY in BACTERIA]) is 1:
            subtitle[-1] += 'was'
        else:
            subtitle[-1] += 'were'

        subtitle[-1] += ' added at t = ' + str(TIME)

    def _add_bacteria(self, bacteria, step):
        bacteria.append((step.get_bacterium_species(), step.get_bacterium_frequency()))

        if step.get_bacterium_species() not in self._bacteria_species:
            self._bacteria_species.append(step.get_bacterium_species())

    def do(self, INITIAL_SUBSTRATE_CONCENTRATION, INITIAL_VOLUME):
        observer = self._OBSERVER_TYPE(self._TIME_FREQUENCY, self._bacteria_species)
        strTrialF = '{:,}'.format(self._TRIAL_FREQUENCY)
        formatStrTrial = '{:>' + str(len(strTrialF)) + ',}'
        floatTrialF = float(self._TRIAL_FREQUENCY)
        strPrecision = str(max(0, len(str(1 / floatTrialF)) - 4))
        formatStrPercent = '{:>' + str(len(('{:.' + strPrecision + '%}').format(1))) + '.' + strPrecision + '%}'

        for trial in xrange(self._TRIAL_FREQUENCY):
            intTrial = 1 + trial
            print ('trial ' + formatStrTrial + ' of ' + strTrialF + ' (' + formatStrPercent + ')').format(intTrial, intTrial / float(floatTrialF))
            time = 0
            chemostat = Chemostat(INITIAL_SUBSTRATE_CONCENTRATION, INITIAL_VOLUME)

            for STEP in self._STEPS:
                STEP.do(time, observer, chemostat)

                try:
                    time += STEP.get_period()
                except NotImplementedError:
                    pass
            observer.observe_trial(chemostat)

        observer.graph(self._subtitle, self._TRIAL_FREQUENCY, INITIAL_SUBSTRATE_CONCENTRATION, self._TIME_FREQUENCY)
