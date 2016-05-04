import math

class Shape(object):
    def S(self, r):
        raise NotImplementedError

    def V(self, r):
        raise NotImplementedError

class Bacillus(Shape):
    fourThirds = 4 / 3.0

    def __init__(self, l):
        self.l = l
        self.a_S = (4 + 2 * l) * math.pi
        self.a_V = (self.fourThirds + l) * math.pi

    def S(self, r):
        return self.a_S * r ** 2

    def V(self, r):
        return self.a_V * r ** 3

def substrateProduct(substrate, coefficient):
    def product(bacterium):
        bacterium.iadd_substrate_f(substrate, coefficient)

    return product

class Enzyme(object):
    """ products is a list of functions that take a bacterium as a parameter. """
    def __init__(self, activeSite_fs, products):
        self.products = products

        self.activeSite_fs = {}

        for substrate in activeSite_fs:
            # The first element is the frequency of unbound active sites for a
            # particular substrate, while the second is the frequency of all
            # active sites for that substrate.
            self.activeSite_fs[substrate] = [activeSite_fs[substrate], activeSite_fs[substrate]]

    def t(self, bacterium):
        catalyze = True

        for substrate in self.activeSite_fs:
            # The frequency of unbound active sites to bind substrate to is the
            # minimum of the frequency of unbound active sites and the
            # frequency of substrate.
            bind_f = min(self.activeSite_fs[substrate][0], bacterium.getSubstrate_f(substrate))

            self.activeSite_fs[substrate][0] -= bind_f
            bacterium.isub_substrate_f(substrate, bind_f)

            # If any active sites are unbound, the enzyme cannot catalyze a
            # reaction.
            if self.activeSite_fs[substrate][0] is not 0:
                catalyze = False

        if catalyze:
            for substrate in self.activeSite_fs:
                self.activeSite_fs[substrate][0] = self.activeSite_fs[substrate][1]

            for product in self.products:
                product(bacterium)

class Bacterium(object):
    def __init__(self, shape, r, enzymes, substrate_fs):
        self.shape = shape
        self.r = r
        self.enzymes = enzymes
        self.substrate_fs = substrate_fs

    def t(self):
        for enzyme in self.enzymes:
            enzyme.t(self)

    def getSubstrate_f(self, substrate):
        return self.substrate_fs[substrate]

    def iadd_substrate_f(self, substrate, other):
        """ substrate_f.__iadd__(other) """
        self.substrate_fs[substrate] += other

    def isub_substrate_f(self, substrate, other):
        """ substrate_f.__isub__(other) """
        self.substrate_fs[substrate] -= other

glucose = substrateProduct('glucose', 1)
fructose = substrateProduct('fructose', 1)
sucrase = Enzyme({'sucrose': 1}, [glucose, fructose])
pC = Bacterium(Bacillus(2), 1, [sucrase for x in xrange(100000)], {'fructose': 0, 'glucose': 0, 'sucrose': 100000})
