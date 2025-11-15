import unittest
import
class CustomTestCase(unittest.TestCase):
    def setUp(self):  # optional
        self.variables = None
    def test_method1(self):
        self.assertTrue(expression, msg=None)
    def test_method2(self):
        executed_value = call_your_func(inputs)
        expected_value = ""
        self.assertEqual(executed_value, expected_value, msg=None)
    def tearDown(self):  # optional
        pass  # default implementation if omitted
if __name__ == '__main__':
    unittest.main()
