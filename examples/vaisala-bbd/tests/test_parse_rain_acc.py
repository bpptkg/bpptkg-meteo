import unittest
from datetime import datetime

from vb.worker import parse_entry


class ProcessLinesTestCase(unittest.TestCase):
    def test_parse_rain_acc(self):
        timestamp = datetime.now()
        lines = [
            b"1R3,Rc=0.01M,Rd=10s,Ri=0.0M,Hc=0.0M,Hd=0s,Hi=0.0M,Rp=185.1M,Hp=2.0M\r\n",
            b"1R2,Ta=21.0C,Tp=21.0C,Ua=94.2P,Pa=872.1H\r\n",
            b"c/address error\r\n",
            b"1R5,Th=24.3C,Vh=0.0#,Vs=12.7V,Vr=3.618V,Id=BBD\r\n",
            b"1R3,Rc=0.02M,Rd=10s,Ri=0.0M,Hc=0.0M,Hd=0s,Hi=0.0M,Rp=185.1M,Hp=2.0M\r\n",
        ]

        entry = parse_entry(timestamp, lines)
        self.assertAlmostEqual(entry["rain_acc"], 0.03, places=4)

    def test_parse_rain_acc_empty(self):
        timestamp = datetime.now()
        lines = [
            b"1R5,Th=24.3C,Vh=0.0#,Vs=12.7V,Vr=3.618V,Id=BBD\r\n",
        ]
        entry = parse_entry(timestamp, lines)
        self.assertIsNone(entry.get("rain_acc"))

    def test_parse_rain_acc_single(self):
        timestamp = datetime.now()
        lines = [
            b"1R3,Rc=0.01M,Rd=10s,Ri=0.0M,Hc=0.0M,Hd=0s,Hi=0.0M,Rp=185.1M,Hp=2.0M\r\n",
        ]
        entry = parse_entry(timestamp, lines)
        self.assertAlmostEqual(entry["rain_acc"], 0.01, places=4)


if __name__ == "__main__":
    unittest.main()
