import unittest

from meteo.parser.vaisala import VaisalaParser


class VaisalaParserTest(unittest.TestCase):

    def test_parsing_1R2(self):
        text = '1R1,Dn=168D,Dm=183D,Dx=208D,Sn=2.8K,Sm=6.3K,Sx=9.3K'
        parser = VaisalaParser()
        s = parser.parse(text)

        self.assertEqual(s['ident'], '1R1')
        self.assertEqual(len(s['components']), 6)

        Dn = s['components'][0]
        self.assertEqual(Dn['field'], 'Dn')
        self.assertEqual(Dn['unit'], 'D')
        self.assertEqual(Dn['text'], 'Dn=168D')

        Sx = s['components'][-1]
        self.assertEqual(Sx['field'], 'Sx')
        self.assertEqual(Sx['unit'], 'K')
        self.assertEqual(Sx['text'], 'Sx=9.3K')

    def test_parsing_1R2(self):
        text = '1R2,Ta=23.0C,Ua=64.8P,Pa=872.5H'
        parser = VaisalaParser()
        s = parser.parse(text)

        self.assertEqual(s['ident'], '1R2')
        self.assertEqual(len(s['components']), 3)

        Ta = s['components'][0]
        self.assertEqual(Ta['field'], 'Ta')
        self.assertEqual(Ta['unit'], 'C')
        self.assertEqual(Ta['text'], 'Ta=23.0C')

        Pa = s['components'][-1]
        self.assertEqual(Pa['field'], 'Pa')
        self.assertEqual(Pa['unit'], 'H')
        self.assertEqual(Pa['text'], 'Pa=872.5H')

    def test_parsing_1R5(self):
        text = '1R5,Th=29.2C,Vh=0.0#,Vs=13.4V,Vr=3.616V,Id=BBD'
        parser = VaisalaParser()
        s = parser.parse(text)

        self.assertEqual(s['ident'], '1R5')
        self.assertEqual(len(s['components']), 5)

        Th = s['components'][0]
        self.assertEqual(Th['field'], 'Th')
        self.assertEqual(Th['unit'], 'C')
        self.assertEqual(Th['text'], 'Th=29.2C')

        Id = s['components'][-1]
        self.assertEqual(Id['field'], 'Id')
        self.assertIsNone(Id['unit'])
        self.assertEqual(Id['text'], 'Id=BBD')


if __name__ == '__main__':
    unittest.main()
