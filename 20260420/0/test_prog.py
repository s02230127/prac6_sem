import unittest
import prog1

class TestSome(unittest.TestCase):
	
	def test_normal(self):
		self.assertEqual(prog1.sqroots("1 1 -2"), "-2.0 1.0")
		
	def test_valueerror(self):
		with self.assertRaises(ValueError):
			prog1.sqroots("ASFSA")
