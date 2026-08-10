# MeshWeaver - ML Function Tests
# Week 2: Test ML/AI function serialization and execution

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
from serializer.task_serializer import TaskSerializer


class TestMLFunctions(unittest.TestCase):
    """Test serialization of ML/AI functions"""
    
    def setUp(self):
        self.serializer = TaskSerializer()
    
    # Test 1: Linear Regression Function
    def test_linear_regression(self):
        """Test serializing a simple linear regression"""
        def linear_regression(X, y):
            # Simple least squares: theta = (X^T X)^-1 X^T y
            X_with_bias = np.column_stack([np.ones(len(X)), X])
            theta = np.linalg.inv(X_with_bias.T @ X_with_bias) @ X_with_bias.T @ y
            return {'intercept': theta[0], 'slope': theta[1]}
        
        X = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        
        task_id, serialized = self.serializer.serialize_task(
            linear_regression, X, y
        )
        result = self.serializer.execute_serialized(serialized)
        
        self.assertAlmostEqual(result['slope'], 2.0, places=5)
        self.assertAlmostEqual(result['intercept'], 0.0, places=5)
        print(f"✅ Linear Regression: slope={result['slope']}, intercept={result['intercept']}")
    
    # Test 2: K-Means Clustering (Simple)
    def test_kmeans_clustering(self):
        """Test serializing k-means clustering logic"""
        def simple_kmeans(data, k=2, iterations=10):
            # Initialize centroids randomly
            np.random.seed(42)
            centroids = data[np.random.choice(len(data), k, replace=False)]
            
            for _ in range(iterations):
                # Assign points to nearest centroid
                distances = np.array([[np.linalg.norm(point - centroid) 
                                     for centroid in centroids] 
                                    for point in data])
                labels = np.argmin(distances, axis=1)
                
                # Update centroids
                for i in range(k):
                    cluster_points = data[labels == i]
                    if len(cluster_points) > 0:
                        centroids[i] = cluster_points.mean(axis=0)
            
            return {'centroids': centroids.tolist(), 'labels': labels.tolist()}
        
        test_data = np.array([[1, 2], [1.5, 1.8], [5, 8], [8, 8], [1, 0.6], [9, 11]])
        
        task_id, serialized = self.serializer.serialize_task(
            simple_kmeans, test_data, k=2, iterations=10
        )
        result = self.serializer.execute_serialized(serialized)
        
        self.assertEqual(len(result['centroids']), 2)
        self.assertEqual(len(result['labels']), 6)
        print(f"✅ K-Means: {len(result['centroids'])} clusters, {len(result['labels'])} points")
    
    # Test 3: Neural Network Activation Functions
    def test_activation_functions(self):
        """Test serializing activation functions"""
        def activation_suite(x):
            # ReLU
            relu = np.maximum(0, x)
            # Sigmoid
            sigmoid = 1 / (1 + np.exp(-x))
            # Tanh
            tanh = np.tanh(x)
            # Softmax
            exp_x = np.exp(x - np.max(x))
            softmax = exp_x / exp_x.sum()
            
            return {
                'relu': relu.tolist(),
                'sigmoid': sigmoid.tolist(),
                'tanh': tanh.tolist(),
                'softmax': softmax.tolist()
            }
        
        test_input = np.array([1.0, 2.0, 3.0, 4.0])
        
        task_id, serialized = self.serializer.serialize_task(
            activation_suite, test_input
        )
        result = self.serializer.execute_serialized(serialized)
        
        self.assertIsNotNone(result['relu'])
        self.assertIsNotNone(result['sigmoid'])
        print(f"✅ Activation Functions: ReLU={result['relu'][0]}, Sigmoid={result['sigmoid'][0]:.4f}")
    
    # Test 4: Gradient Descent
    def test_gradient_descent(self):
        """Test serializing gradient descent optimization"""
        def gradient_descent(X, y, learning_rate=0.01, iterations=100):
            m, n = X.shape
            theta = np.zeros(n)
            
            for _ in range(iterations):
                predictions = X @ theta
                errors = predictions - y
                gradient = (1/m) * (X.T @ errors)
                theta -= learning_rate * gradient
            
            return {'weights': theta.tolist(), 'iterations': iterations}
        
        X = np.array([[1, 1], [1, 2], [1, 3], [1, 4]])
        y = np.array([2, 4, 6, 8])
        
        task_id, serialized = self.serializer.serialize_task(
            gradient_descent, X, y, learning_rate=0.01, iterations=100
        )
        result = self.serializer.execute_serialized(serialized)
        
        self.assertEqual(len(result['weights']), 2)
        print(f"✅ Gradient Descent: weights={result['weights']}")
    
    # Test 5: Decision Tree Prediction
    def test_decision_tree_logic(self):
        """Test serializing decision tree prediction logic"""
        def predict_with_tree(features):
            # Simple hardcoded decision tree for iris-like data
            if features[0] < 5.5:
                if features[1] < 3.0:
                    return 'Class A'
                else:
                    return 'Class B'
            else:
                if features[2] > 4.5:
                    return 'Class C'
                else:
                    return 'Class B'
        
        test_features = [5.0, 3.5, 1.4, 0.2]
        
        task_id, serialized = self.serializer.serialize_task(
            predict_with_tree, test_features
        )
        result = self.serializer.execute_serialized(serialized)
        
        self.assertIn('Class', result)
        print(f"✅ Decision Tree: Predicted {result}")
    
    # Test 6: Feature Engineering
    def test_feature_engineering(self):
        """Test serializing feature engineering pipeline"""
        def engineer_features(data):
            # Normalize
            normalized = (data - np.mean(data)) / np.std(data)
            # Polynomial features
            squared = data ** 2
            cubed = data ** 3
            # Interactions
            pairwise = data[:, np.newaxis] * data
            
            return {
                'normalized': normalized.tolist(),
                'squared': squared.tolist(),
                'cubed': cubed.tolist(),
                'mean': float(np.mean(data)),
                'std': float(np.std(data))
            }
        
        test_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        task_id, serialized = self.serializer.serialize_task(
            engineer_features, test_data
        )
        result = self.serializer.execute_serialized(serialized)
        
        self.assertEqual(len(result['normalized']), 5)
        self.assertAlmostEqual(result['mean'], 3.0)
        print(f"✅ Feature Engineering: mean={result['mean']}, std={result['std']:.2f}")


if __name__ == '__main__':
    print("=== MeshWeaver Week 2: ML Function Tests ===\n")
    unittest.main(verbosity=2)
