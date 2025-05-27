import os
import unittest
from typing import List

from dev_observer.api.types.observations_pb2 import ObservationKey, Observation
from dev_observer.observations.local import LocalObservationsProvider


class TestLocalObservationsProvider(unittest.IsolatedAsyncioTestCase):
    async def test_list_files(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        o = LocalObservationsProvider(root_dir=os.path.join(current_dir, "test_data"))
        result = await o.list("repos")
        self.assertEqual(len(result), 2)
        k0 = result[0]
        k1 = result[1]
        self.assertEqual(ObservationKey(kind="repos", name="a.md", key="a.md"), k0)
        self.assertEqual(ObservationKey(kind="repos", name="c.md", key="b/c.md"), k1)
        o0 = await o.get(k0)
        self.assertEqual(Observation(key=k0, content=b'test_a'), o0)
        o1 = await o.get(k1)
        self.assertEqual(Observation(key=k1, content=b'test_c'), o1)

    async def test_int_conversion(self):
        b = "Tbbb".encode("utf-8")
        res: int = 0
        for c in b:
            res = (res << 8) + int(c)
        self.assertEqual(1415733858, res)

        tb: List[int] = []
        tc = 1415733858
        while tc > 0:
            tb.append(tc % 256)
            tc = tc >> 8
        tb.reverse()
        st_b = bytes(tb)
        self.assertEqual("Tbbb", st_b.decode("utf-8"))
