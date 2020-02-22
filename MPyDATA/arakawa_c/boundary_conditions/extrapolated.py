from ...utils import debug_flag

if debug_flag.VALUE:
    import MPyDATA.utils.fake_numba as numba
else:
    import numba

# TODO: allow passing from caller scope
eps = 1e-10


class ExtrapolatedLeft:

    @staticmethod
    @numba.njit
    def scalar(impl, d):
        assert d == 0

        a = impl.data
        edg = impl.left_edge(d).start
        nom = a[edg+1] - a[edg]
        den = a[edg+2] - a[edg+1]
        cnst = nom/den if abs(den) > eps else 0

        for i in range(impl.left_halo(d).stop-1, impl.left_halo(d).start-1, -1):
            value = max(a[i+1] - (a[i+2] - a[i+1]) * cnst, 0)
            a[i] = value

    @staticmethod
    @numba.njit
    def vector(impl, axis, comp):
        lh = impl.left_halo(axis, comp)
        le = impl.left_edge(axis, comp)
        for i in range(lh.start, lh.stop):
            impl.data(comp)[i] = impl.data(comp)[le.start]


class ExtrapolatedRight:
    @staticmethod
    @numba.njit
    def scalar(impl, d):
        assert d == 0

        a = impl.data
        edg = impl.right_edge(0).stop - 1
        den = a[edg - 1] - a[edg - 2]
        nom = a[edg] - a[edg - 1]
        cnst = nom/den if abs(den) > eps else 0

        for i in range(impl.right_halo(d).start, impl.right_halo(d).stop):
            value = max(a[i - 1] + (a[i - 1] - a[i - 2]) * cnst, 0)
            a[i] = value

    @staticmethod
    @numba.njit
    def vector(impl, axis, comp):
        rh = impl.right_halo(axis, comp)
        re = impl.right_edge(axis, comp)
        for i in range(rh.start, rh.stop):
            impl.data(comp)[i] = re.stop-1
