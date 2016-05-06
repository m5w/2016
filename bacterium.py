class Bacterium(object):
    def __init__(self, s_r_2_a, r, v_r_3_a, min_atp_r_3_a, s_atp,
            fission_atp_r_2_a, fission_atp_r_3_a):
        self._s_is_cached = False
        self._s_r_2_a = s_r_2_a
        self._r = r
        self._v_is_cached = False
        self._v_r_3_a = v_r_3_a
        self._min_atp_is_cached = False
        self._min_atp_r_3_a = min_atp_r_3_a
        self._fission_atp_is_cached = False
        self._s_atp = s_atp
        self._fission_atp_r_2_a = fission_atp_r_2_a
        self._fission_atp_r_3_a = fission_atp_r_3_a

    def _get_s(self):
        if self._s_is_cached:
            return self._s

        self._s = self._s_r_2_a * self._r ** 2
        self._s_is_cached = True
        return self._s

    def _get_v(self):
        if self._v_is_cached:
            return self._v

        self._v = self._v_r_3_a * self._r ** 3
        self._v_is_cached = True
        return self._v

    def _get_min_atp(self):
        if self._min_atp_is_cached:
            return self._min_atp

        self._min_atp = self._min_atp_r_3_a * self._get_v()
        self._min_atp_is_cached = True
        return self._min_atp

    def _get_fission_atp(self):
        if self._fission_atp_is_cached:
            return self._fission_atp

        self._fission_atp = (self._s_atp + self._fission_atp_r_2_a *
                self._get_s() + self._fission_atp_r_3_a * self._get_v())
        self._fission_atp_is_cached = True
        return self._fission_atp

    def t(self, p):
