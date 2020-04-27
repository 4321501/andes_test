import unittest

from andes.core.var import Algeb
from andes.core.param import NumParam, DummyValue
from andes.core.discrete import Limiter, SortedLimiter, Switcher, Delay
from andes.shared import np


class TestDiscrete(unittest.TestCase):
    def setUp(self):
        self.lower = NumParam()
        self.upper = NumParam()
        self.u = Algeb()

        self.upper.v = np.array([2,    2,   2, 2,   2,   2, 2.8, 3.9])
        self.u.v = np.array([-3, -1.1,  -5, 0,   1,   2,   3,  10])
        self.lower.v = np.array([-2,   -1, 0.5, 0, 0.5, 1.5,   2,   3])

    def test_limiter(self):
        """
        Tests for `Limiter` class
        Returns
        -------

        """
        self.cmp = Limiter(self.u, self.lower, self.upper)
        self.cmp.list2array(len(self.u.v))

        self.cmp.check_var()

        self.assertSequenceEqual(self.cmp.zl.tolist(),
                                 [1., 1., 1., 1., 0., 0., 0., 0.])
        self.assertSequenceEqual(self.cmp.zi.tolist(),
                                 [0., 0., 0., 0., 1., 0., 0., 0.])
        self.assertSequenceEqual(self.cmp.zu.tolist(),
                                 [0., 0., 0., 0., 0., 1., 1., 1.])

    def test_sorted_limiter(self):
        """
        Tests for `SortedLimiter` class

        Returns
        -------

        """
        self.cmp = Limiter(self.u, self.lower, self.upper)
        self.cmp.list2array(len(self.u.v))
        self.cmp.check_var()

        self.rcmp = SortedLimiter(self.u, self.lower, self.upper, n_select=1)
        self.rcmp.list2array(len(self.u.v))
        self.rcmp.check_var()

        self.assertSequenceEqual(self.rcmp.zl.tolist(),
                                 [0., 0., 1., 0., 0., 0., 0., 0.])
        self.assertSequenceEqual(self.rcmp.zi.tolist(),
                                 [1., 1., 0., 1., 1., 1., 1., 0.])
        self.assertSequenceEqual(self.rcmp.zu.tolist(),
                                 [0., 0., 0., 0., 0., 0., 0., 1.])

        # test when no `n_select` is specified
        self.rcmp_noselect = SortedLimiter(self.u, self.lower, self.upper)
        self.rcmp_noselect.list2array(len(self.u.v))
        self.rcmp_noselect.check_var()

        self.assertSequenceEqual(self.rcmp_noselect.zl.tolist(),
                                 self.cmp.zl.tolist())
        self.assertSequenceEqual(self.rcmp_noselect.zi.tolist(),
                                 self.cmp.zi.tolist())
        self.assertSequenceEqual(self.rcmp_noselect.zu.tolist(),
                                 self.cmp.zu.tolist())

        # test when no `n_select` is over range
        self.rcmp_noselect = SortedLimiter(self.u, self.lower, self.upper,
                                           n_select=999)
        self.rcmp_noselect.list2array(len(self.u.v))
        self.rcmp_noselect.check_var()

        self.assertSequenceEqual(self.rcmp_noselect.zl.tolist(),
                                 self.cmp.zl.tolist())
        self.assertSequenceEqual(self.rcmp_noselect.zi.tolist(),
                                 self.cmp.zi.tolist())
        self.assertSequenceEqual(self.rcmp_noselect.zu.tolist(),
                                 self.cmp.zu.tolist())

    def test_switcher(self):
        p = NumParam()
        p.v = np.array([0, 1, 2, 2, 1, 3, 1])
        switcher = Switcher(u=p, options=[0, 1, 2, 3, 4])
        switcher.list2array(len(p.v))

        switcher.check_var()

        self.assertSequenceEqual(switcher.s0.tolist(), [1, 0, 0, 0, 0, 0, 0])
        self.assertSequenceEqual(switcher.s1.tolist(), [0, 1, 0, 0, 1, 0, 1])
        self.assertSequenceEqual(switcher.s2.tolist(), [0, 0, 1, 1, 0, 0, 0])
        self.assertSequenceEqual(switcher.s3.tolist(), [0, 0, 0, 0, 0, 1, 0])
        self.assertSequenceEqual(switcher.s4.tolist(), [0, 0, 0, 0, 0, 0, 0])


class TestDelay(unittest.TestCase):
    def setUp(self) -> None:
        self.n = 5   # number of input values to delay
        self.step = 2

        self.time = 1.0  # delay period in second
        self.data = DummyValue(0)
        self.data.v = np.zeros(self.n)

        self.dstep = Delay(u=self.data, mode='step', delay=self.step)
        self.dstep.list2array(self.n)

        self.dtime = Delay(u=self.data, mode='time', delay=self.time)
        self.dtime.list2array(self.n)

        self.v = self.dstep.v
        self.vt = self.dtime.v

    def test_delay_step(self):
        n_forward = 5
        for i in range(n_forward):
            self.dstep.check_var(i)
            self.data.v += 1

        self.assertSequenceEqual(self.v.tolist(), [n_forward - self.step - 1] * self.n)

    def test_delay_time(self):
        n_forward = 10
        tstep = 0.2
        dae_t = 0
        for i in range(n_forward):
            self.data.v[:] = dae_t
            self.dtime.check_var(dae_t)
            dae_t += tstep

        np.testing.assert_almost_equal(self.vt, [(n_forward - 1) * tstep - self.time] * self.n)


