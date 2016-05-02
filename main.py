class Enzyme(object):
    """ products is a list of functions that take a cell as a parameter. """
    def __init__(self, activeSite_fs, products):
        self.products = products

        self.activeSite_fs = {}

        for substrate in self.activeSite_fs:
            # The first element is the frequency of unbound active sites for a
            # particular substrate, while the second is the frequency of all
            # active sites for that substrate.
            self.activeSite_fs[substrate] = [activeSite_fs[substrate], activeSite_fs[substrate]]

    def t(self, cell):
        catalyze = True

        for substrate in self.activeSite_fs:
            # The frequency of unbound active sites to bind substrate to is the
            # minimum of the frequency of unbound active sites and the
            # frequency of substrate.
            bind_f = min(self.activeSite_fs[substrate][0], cell.getSubstrate_f(substrate))

            self.activeSite_fs[substrate][0] -= bind_f
            cell.isub_substrate_f(substrate, bind_f)

            # If any active sites are unbound, the enzyme cannot catalyze a
            # reaction.
            if self.activeSite_fs[substrate][0] is not 0:
                catalyze = False

        if catalyze:
            for substrate in self.activeSite_fs:
                self.activeSite_fs[substrate][0] = self.activeSite_fs[substrate][1]

            for product in self.products:
                product(cell)

class Cell(object):
    def getSubstrate_f(self, substrate):
        raise NotImplementedError

    def isub_substrate_f(self, substrate, other):
        """ substrate_f.__isub__(other) """
        raise NotImplementedError
