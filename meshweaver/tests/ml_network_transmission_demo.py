# MeshWeaver - Week 2 Complete Demo
# Serialization Check: Transmit and Execute Complex ML/Math Functions

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from serializer.task_serializer import TaskSerializer
from serializer.task_queue import DistributedTaskQueue
from serializer.ml_functions import (
    logistic_regression_train,
    k_nearest_neighbors,
    pca_transform,
    time_series_features,
    neural_network_forward
)


class Week2Demo:
    """Complete Week 2 demonstration of serialization across network"""
    
    def __init__(self):
        self.serializer = TaskSerializer()
        self.node1 = DistributedTaskQueue("ML-Node-1")
        self.node2 = DistributedTaskQueue("Math-Node-2")
    
    def demo_1_basic_serialization(self):
        """Demo 1: Basic function serialization"""
        print("\n" + "="*60)
        print("DEMO 1: Basic Math Function Serialization")
        print("="*60)
        
        def matrix_multiply(A, B):
            return (A @ B).tolist()
        
        A = np.array([[1, 2], [3, 4]])
        B = np.array([[5, 6], [7, 8]])
        
        task_id, serialized = self.serializer.serialize_task(matrix_multiply, A, B)
        result = self.serializer.execute_serialized(serialized)
        
        print(f"Matrix A:\n{A}")
        print(f"Matrix B:\n{B}")
        print(f"Result:\n{np.array(result)}")
        print("✅ Basic serialization successful!")
    
    def demo_2_ml_function_transmission(self):
        """Demo 2: ML function transmission"""
        print("\n" + "="*60)
        print("DEMO 2: ML Function Transmission")
        print("="*60)
        
        # Generate training data
        np.random.seed(42)
        X = np.random.rand(100, 3)
        y = (X[:, 0] + X[:, 1] > 1).astype(int)
        
        print("Training logistic regression model...")
        task_id, serialized = self.serializer.serialize_task(
            logistic_regression_train, X, y, learning_rate=0.1, iterations=100
        )
        
        # Simulate network transmission
        print("📡 Transmitting function over network...")
        result = self.serializer.execute_serialized(serialized)
        
        print(f"Final Loss: {result['final_loss']:.4f}")
        print(f"Weights: {[f'{w:.3f}' for w in result['weights']]}")
        print(f"Bias: {result['bias']:.3f}")
        print("✅ ML function transmitted and executed!")
    
    def demo_3_knn_classification(self):
        """Demo 3: KNN classification serialization"""
        print("\n" + "="*60)
        print("DEMO 3: K-Nearest Neighbors Classification")
        print("="*60)
        
        X_train = np.array([[1, 2], [2, 3], [3, 4], [6, 7], [7, 8], [8, 9]])
        y_train = np.array([0, 0, 0, 1, 1, 1])
        X_test = np.array([[2, 2], [7, 7], [4, 5]])
        
        task_id, serialized = self.serializer.serialize_task(
            k_nearest_neighbors, X_train, y_train, X_test, k=3
        )
        
        print("📡 Transmitting KNN function...")
        predictions = self.serializer.execute_serialized(serialized)
        
        print(f"Test Points: {X_test.tolist()}")
        print(f"Predictions: {predictions}")
        print("✅ KNN classification successful!")
    
    def demo_4_pca_dimensionality_reduction(self):
        """Demo 4: PCA dimensionality reduction"""
        print("\n" + "="*60)
        print("DEMO 4: PCA Dimensionality Reduction")
        print("="*60)
        
        # High-dimensional data
        X = np.random.rand(50, 10)
        
        task_id, serialized = self.serializer.serialize_task(
            pca_transform, X, n_components=3
        )
        
        print("📡 Transmitting PCA function...")
        result = self.serializer.execute_serialized(serialized)
        
        print(f"Original dimensions: 10")
        print(f"Reduced dimensions: 3")
        print(f"Explained variance: {[f'{v:.2%}' for v in result['explained_variance']]}")
        print(f"Total variance explained: {result['total_variance_explained']:.2%}")
        print("✅ PCA reduction successful!")
    
    def demo_5_neural_network(self):
        """Demo 5: Neural network forward pass"""
        print("\n" + "="*60)
        print("DEMO 5: Neural Network Forward Pass")
        print("="*60)
        
        # Input data
        X = np.random.rand(5, 4)  # 5 samples, 4 features
        
        # Network parameters
        W1 = np.random.randn(4, 8)
        b1 = np.zeros(8)
        W2 = np.random.randn(8, 1)
        b2 = np.zeros(1)
        
        task_id, serialized = self.serializer.serialize_task(
            neural_network_forward, X, W1, b1, W2, b2
        )
        
        print("📡 Transmitting neural network function...")
        result = self.serializer.execute_serialized(serialized)
        
        print(f"Input shape: {X.shape}")
        print(f"Hidden layer size: 8")
        print(f"Output: {[f'{v[0]:.4f}' for v in result['output']]}")
        print(f"Mean output: {result['mean_output']:.4f}")
        print("✅ Neural network forward pass successful!")
    
    def demo_6_time_series_analysis(self):
        """Demo 6: Time series feature extraction"""
        print("\n" + "="*60)
        print("DEMO 6: Time Series Feature Extraction")
        print("="*60)
        
        # Generate random walk time series
        np.random.seed(42)
        series = np.random.randn(200).cumsum()
        
        task_id, serialized = self.serializer.serialize_task(
            time_series_features, series
        )
        
        print("📡 Transmitting time series function...")
        result = self.serializer.execute_serialized(serialized)
        
        print(f"Series length: {len(series)}")
        print(f"Mean: {result['mean']:.2f}")
        print(f"Std Dev: {result['std']:.2f}")
        print(f"Range: {result['range']:.2f}")
        print(f"Skewness: {result['skewness']:.2f}")
        print(f"Kurtosis: {result['kurtosis']:.2f}")
        print("✅ Time series analysis successful!")
    
    async def demo_7_async_multi_node(self):
        """Demo 7: Async multi-node execution"""
        print("\n" + "="*60)
        print("DEMO 7: Async Multi-Node Task Distribution")
        print("="*60)
        
        def task_eigenvalues(matrix):
            eigenvalues = np.linalg.eigvals(matrix)
            return {
                'eigenvalues': eigenvalues.tolist(),
                'max_eigenvalue': float(np.max(eigenvalues.real))
            }
        
        def task_svd(matrix):
            U, S, Vt = np.linalg.svd(matrix)
            return {
                'singular_values': S.tolist(),
                'rank': len(S)
            }
        
        # Create test matrices
        matrix1 = np.random.rand(5, 5)
        matrix2 = np.random.rand(5, 5)
        
        # Submit to different nodes
        print("Submitting eigenvalue task to Node 1...")
        await self.node1.submit(task_eigenvalues, matrix1, priority=1)
        
        print("Submitting SVD task to Node 2...")
        await self.node2.submit(task_svd, matrix2, priority=1)
        
        # Execute concurrently
        print("\n📡 Executing tasks on multiple nodes...")
        task1 = await self.node1.execute_next()
        task2 = await self.node2.execute_next()
        
        print(f"\nNode 1 Result (Eigenvalues):")
        print(f"  Max eigenvalue: {task1.result['max_eigenvalue']:.4f}")
        
        print(f"\nNode 2 Result (SVD):")
        print(f"  Rank: {task2.result['rank']}")
        print(f"  Singular values: {[f'{s:.3f}' for s in task2.result['singular_values']]}")
        
        print("\n✅ Multi-node execution successful!")
    
    def demo_8_complex_closure(self):
        """Demo 8: Serializing complex closures"""
        print("\n" + "="*60)
        print("DEMO 8: Complex Closure Serialization")
        print("="*60)
        
        def create_ml_pipeline(scaler_type='standard'):
            """Factory function creating ML pipeline"""
            def pipeline(X):
                # Scale data
                if scaler_type == 'standard':
                    X_scaled = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
                else:  # minmax
                    X_scaled = (X - np.min(X, axis=0)) / (np.max(X, axis=0) - np.min(X, axis=0))
                
                # Apply transformation
                X_transformed = X_scaled ** 2
                
                return {
                    'scaled': X_scaled.tolist(),
                    'transformed': X_transformed.tolist(),
                    'scaler_type': scaler_type
                }
            return pipeline
        
        # Create pipeline with closure
        standard_pipeline = create_ml_pipeline('standard')
        X = np.random.rand(10, 3)
        
        task_id, serialized = self.serializer.serialize_task(standard_pipeline, X)
        
        print("📡 Transmitting pipeline with closure...")
        result = self.serializer.execute_serialized(serialized)
        
        print(f"Scaler type: {result['scaler_type']}")
        print(f"Input shape: {X.shape}")
        print(f"Output shape: {np.array(result['transformed']).shape}")
        print("✅ Complex closure serialization successful!")
    
    def run_all_demos(self):
        """Run all demonstrations"""
        print("\n" + "="*70)
        print(" "*15 + "MESHWEAVER - WEEK 2 DEMO")
        print(" "*5 + "Serialization Check: Complex ML/Math Functions")
        print("="*70)
        
        self.demo_1_basic_serialization()
        self.demo_2_ml_function_transmission()
        self.demo_3_knn_classification()
        self.demo_4_pca_dimensionality_reduction()
        self.demo_5_neural_network()
        self.demo_6_time_series_analysis()
        
        # Async demo
        asyncio.run(self.demo_7_async_multi_node())
        
        self.demo_8_complex_closure()
        
        print("\n" + "="*70)
        print(" "*20 + "🎉 ALL DEMOS COMPLETE! 🎉")
        print("="*70)
        print("\n✅ Week 2 Task Accomplished:")
        print("   - Serialized complex ML/Math functions")
        print("   - Transmitted functions across simulated network")
        print("   - Executed functions remotely and retrieved results")
        print("   - Tested with: Regression, KNN, PCA, Neural Nets, Time Series")
        print("   - Verified multi-node async execution")
        print("="*70 + "\n")


if __name__ == "__main__":
    demo = Week2Demo()
    demo.run_all_demos()
