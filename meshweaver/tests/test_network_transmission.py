# MeshWeaver - Network Transmission Tests
# Week 2: Test function transmission across simulated network

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import asyncio
import numpy as np
from serializer.task_serializer import TaskSerializer
from serializer.task_queue import DistributedTaskQueue


class TestNetworkTransmission(unittest.TestCase):
    """Test transmitting serialized functions across network simulation"""
    
    def setUp(self):
        self.serializer = TaskSerializer()
    
    # Test 1: Simulate Network Transmission
    def test_simulated_network_transmission(self):
        """Simulate sending serialized task over network"""
        def complex_computation(matrix, vector):
            result = matrix @ vector
            return result.tolist()
        
        matrix = np.array([[1, 2], [3, 4]])
        vector = np.array([5, 6])
        
        # Serialize (sender side)
        task_id, serialized_bytes = self.serializer.serialize_task(
            complex_computation, matrix, vector
        )
        
        # Simulate network transmission
        transmitted_data = serialized_bytes  # In real network: socket.send(serialized_bytes)
        
        # Deserialize (receiver side)
        result = self.serializer.execute_serialized(transmitted_data)
        
        expected = [17, 39]  # matrix @ vector
        self.assertEqual(result, expected)
        print(f"✅ Network Transmission: {result}")
    
    # Test 2: Multi-Node Task Distribution
    def test_async_multi_node_execution(self):
        """Test async task distribution across multiple nodes"""
        async def run_multi_node():
            # Create multiple "nodes"
            node1 = DistributedTaskQueue("node-1")
            node2 = DistributedTaskQueue("node-2")
            
            def ml_task_1(data):
                return np.mean(data)
            
            def ml_task_2(data):
                return np.std(data)
            
            # Submit tasks to different nodes
            data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            
            await node1.submit(ml_task_1, data, priority=1)
            await node2.submit(ml_task_2, data, priority=1)
            
            # Execute on both nodes
            task1 = await node1.execute_next()
            task2 = await node2.execute_next()
            
            return task1.result, task2.result
        
        mean_result, std_result = asyncio.run(run_multi_node())
        
        self.assertAlmostEqual(mean_result, 5.5)
        self.assertGreater(std_result, 0)
        print(f"✅ Multi-Node: mean={mean_result}, std={std_result:.2f}")
    
    # Test 3: Large Data Serialization
    def test_large_data_transmission(self):
        """Test transmitting large datasets"""
        def process_large_matrix(matrix):
            eigenvalues = np.linalg.eigvals(matrix)
            return {
                'size': matrix.shape,
                'eigenvalues_mean': float(np.mean(eigenvalues.real)),
                'determinant': float(np.linalg.det(matrix))
            }
        
        # Create large matrix (100x100)
        large_matrix = np.random.rand(100, 100)
        
        task_id, serialized = self.serializer.serialize_task(
            process_large_matrix, large_matrix
        )
        
        # Check serialization succeeded
        self.assertIsNotNone(serialized)
        
        result = self.serializer.execute_serialized(serialized)
        self.assertEqual(result['size'], (100, 100))
        print(f"✅ Large Data: {result['size']}, det={result['determinant']:.4f}")
    
    # Test 4: Function with External Dependencies
    def test_function_with_imports(self):
        """Test serializing functions that import libraries"""
        def scientific_computation(x):
            import scipy.stats as stats
            import numpy as np
            
            # Normal distribution analysis
            mean = np.mean(x)
            std = np.std(x)
            
            # Statistical tests
            normality = stats.normaltest(x)
            
            return {
                'mean': float(mean),
                'std': float(std),
                'is_normal': normality.pvalue > 0.05
            }
        
        test_data = np.random.normal(0, 1, 100)
        
        task_id, serialized = self.serializer.serialize_task(
            scientific_computation, test_data
        )
        result = self.serializer.execute_serialized(serialized)
        
        self.assertIn('mean', result)
        self.assertIn('is_normal', result)
        print(f"✅ External Deps: mean={result['mean']:.2f}, normal={result['is_normal']}")
    
    # Test 5: Error Handling in Network Transmission
    def test_transmission_error_handling(self):
        """Test handling errors during transmission"""
        def failing_function(x):
            if x < 0:
                raise ValueError("Negative values not allowed")
            return x ** 2
        
        # Test successful case
        task_id1, serialized1 = self.serializer.serialize_task(failing_function, 5)
        result1 = self.serializer.execute_serialized(serialized1)
        self.assertEqual(result1, 25)
        
        # Test error case
        task_id2, serialized2 = self.serializer.serialize_task(failing_function, -5)
        result2 = self.serializer.execute_serialized(serialized2)
        self.assertIsNone(result2)  # Should return None on error
        
        print(f"✅ Error Handling: success={result1}, error=handled")
    
    # Test 6: Concurrent Task Execution
    def test_concurrent_execution(self):
        """Test executing multiple tasks concurrently"""
        async def run_concurrent():
            queue = DistributedTaskQueue("concurrent-node")
            
            def task_a(x): return x * 2
            def task_b(x): return x ** 2
            def task_c(x): return x + 100
            
            # Submit multiple tasks
            await queue.submit(task_a, 10, priority=1)
            await queue.submit(task_b, 5, priority=1)
            await queue.submit(task_c, 7, priority=1)
            
            # Execute all
            await queue.run_all()
            
            return [t.result for t in queue.completed]
        
        results = asyncio.run(run_concurrent())
        
        self.assertEqual(len(results), 3)
        self.assertIn(20, results)  # task_a(10)
        self.assertIn(25, results)  # task_b(5)
        self.assertIn(107, results)  # task_c(7)
        print(f"✅ Concurrent Execution: {results}")


if __name__ == '__main__':
    print("=== MeshWeaver Week 2: Network Transmission Tests ===\n")
    unittest.main(verbosity=2)
