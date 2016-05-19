import main

import pylab

period_step = main.PeriodStep(1000, 0.0, 0.0, 0.0)

caudatum_mu = main.get_specific_growth_rate_monod(0.5, 1.0)
caudatum = main.BacteriumSpecies('P. caudatum', 1.0, 0.001, main.get_growth_rate_monod(caudatum_mu), main.get_substrate_consumption_rate_monod(1000.0, caudatum_mu))
caudatum_step = main.BacteriaStep(caudatum, 10)
caudatum_procedure = main.Procedure([caudatum_step, period_step], 10, main.TimeMeanBacteriumSpeciesFrequencyObserver)

aurelia_mu = main.get_specific_growth_rate_monod(1.0, 1.0)
aurelia = main.BacteriumSpecies('P. aurelia', 1.0, 0.001, main.get_growth_rate_monod(aurelia_mu), main.get_substrate_consumption_rate_monod(1000.0, aurelia_mu))
aurelia_step = main.BacteriaStep(aurelia, 10)
aurelia_procedure = main.Procedure([aurelia_step, period_step], 10, main.TimeMeanBacteriumSpeciesFrequencyObserver)

procedure = main.Procedure([caudatum_step, aurelia_step, period_step], 10, main.TimeMeanBacteriumSpeciesFrequencyObserver)

alpha = main.BacteriumSpecies('alpha', 2.0, 0.001, main.get_growth_rate_monod(caudatum_mu), main.get_substrate_consumption_rate_monod(1000.0, caudatum_mu))
alpha_step = main.BacteriaStep(alpha, 10)
alpha_procedure = main.Procedure([caudatum_step, alpha_step, period_step], 10, main.TimeMeanBacteriumSpeciesFrequencyObserver)

beta = main.BacteriumSpecies('beta', 2.0, 0.001, main.get_growth_rate_monod(aurelia_mu), main.get_substrate_consumption_rate_monod(1000.0, aurelia_mu))
beta_step = main.BacteriaStep(beta, 10)
beta_procedure = main.Procedure([caudatum_step, beta_step, period_step], 10, main.TimeMeanBacteriumSpeciesFrequencyObserver)
