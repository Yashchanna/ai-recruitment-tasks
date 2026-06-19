import unittest
from task3_architecture_pipeline.src import parser

class TestParser(unittest.TestCase):
    def test_extract_entities(self):
        req = 'Small web app with auth, products, orders and payments and image uploads'
        res = parser.analyze_requirements(req)
        self.assertIn('product', res['entities'])
        self.assertIn('auth', res['entities'])
        self.assertIn('order', res['entities'])
        self.assertIn('payment', res['entities'])
        self.assertIn('image', res['entities'])
        self.assertGreaterEqual(res['confidence'], 0.1)

    def test_constraints(self):
        req = 'Highly available, low latency streaming service with realtime updates'
        res = parser.analyze_requirements(req)
        # realtime should be detected as a constraint
        self.assertIn('realtime', res['constraints'])

if __name__ == '__main__':
    unittest.main()
