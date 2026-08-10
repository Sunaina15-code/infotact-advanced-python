# MeshWeaver - Serialization Tests
# Week 2: Test basic serialization of complex functions

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
from serializer.task_serializer import TaskSerializer


class TestSerialization(unittest.TestCase):
    """Test serialization of various function types"""
    
    def setUp(self):
        self.serializer = TaskSerializer()
    
    # Test 1: Simple Math Function
    def test_simple_math_function(self):
        """Test serializing a simple mathematical function"""
        def calculate_quadratic(a, b, c, x):
            return a * x**2 + b * x + c
        
        task_id, serialized = self.serializer.serialize_task(
            calculate_quadratic, 2, 3, 1, 5
        )
        self.assertIsNotNone(serialized)
        
        result = self.serializer.execute_serialized(serialized)
        expected = 2 * 5**2 + 3 * 5 + 1  # 66
        self.assertEqual(result, expected)
        print(f"✅ Quadratic function: {result}")
    
    # Test 2: Lambda Function
    def test_lambda_serialization(self):
        """Test serializing lambda functions"""
        factorial = lambda n: 1 if n == 0 else n * factorial(n-1)
        
        task_id, serialized = self.serializer.serialize_task(factorial, 5)
        self.assertIsNotNone(serialized)
        
        result = self.serializer.execute_serialized(serialized)
        self.assertEqual(result, 120)
        print(f"✅ Lambda factorial: {result}")
    
    # Test 3: Function with Closures
    def test_closure_serialization(self):
        """Test serializing functions with closures"""
        def make_multiplier(factor):
            def multiply(x):
                return x * factor
            return multiply
        
        times_ten = make_multiplier(10)
        task_id, serialized = self.serializer.serialize_task(times_ten, 7)
        result = self.serializer.execute_serialized(serialized)
        
        self.assertEqual(result, 70)
        print(f"✅ Closure function: {result}")
    
    # Test 4: Numpy Array Operations
    def test_numpy_serialization(self):
        """Test serializing NumPy operations"""
        def matrix_operations(matrix):
            return {
                'mean': np.mean(matrix),
                'std': np.std(matrix),
                'sum': np.sum(matrix),
                'shape': matrix.shape
            }
        
        test_matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        task_id, serialized = self.serializer.serialize_task(
            matrix_operations, test_matrix
        )
        result = self.serializer.execute_serialized(serialized)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['mean'], 5.0)
        self.assertEqual(result['shape'], (3, 3))
        print(f"✅ NumPy operations: mean={result['mean']}, shape={result['shape']}")
    
    # Test 5: Complex Math Function
    def test_complex_math_function(self):
        """Test serializing complex mathematical computations"""
        def calculate_statistics(data):
            import math
            n = len(data)
            mean = sum(data) / n
            variance = sum((x - mean) ** 2 for x in data) / n
            std_dev = math.sqrt(variance)
            
            return {
                'count': n,
                'mean': mean,
                'variance': variance,
                'std_dev': std_dev,
                'min': min(data),
                'max': max(data)
            }
        
        test_data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        task_id, serialized = self.serializer.serialize_task(
            calculate_statistics, test_data
        )
        result = self.serializer.execute_serialized(serialized)
        
        self.assertEqual(result['count'], 10)
        self.assertEqual(result['mean'], 55.0)
        self.assertEqual(result['min'], 10)
        self.assertEqual(result['max'], 100)
        print(f"✅ Statistics: mean={result['mean']}, std={result['std_dev']:.2f}")


if __name__ == '__main__':
    print("=== MeshWeaver Week 2: Serialization Tests ===\n")
    unittest.main(verbosity=2)
