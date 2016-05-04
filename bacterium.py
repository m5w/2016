class Bacterium(object):
    """ a is the inradius' square's coefficient in the formula for surface
    area, since _surface_area_inradius_square_coefficient is too long a
    variable name to use. """
    def __init__(self, surface_area_a, inradius, volume_a):
        self._surface_area_is_cached = False
        self._surface_area_a = surface_area_a
        self._inradius = inradius
        self._volume_is_cached = False
        self._volume_a = volume_a

    def _return_surface_area(self):
        if self._surface_area_is_cached:
            return self._surface_area

        self._surface_area = self._a * self._inradius ** 2
        self._surface_area_is_cached = True
        return self._surface_area

    def _return_volume(self):
        if self._volume_is_cached:
            return self._volume

        self._volume = self._inradius ** 3
        self._volume_is_cached = True
        return self._volume
