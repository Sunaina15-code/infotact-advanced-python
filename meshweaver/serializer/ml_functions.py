# MeshWeaver - ML Functions Library
# Week 2: Complex ML/Math functions for testing

import numpy as np
from typing import Dict, List, Tuple


def linear_model(X: np.ndarray, weights: np.ndarray, bias: float) -> np.ndarray:
    """Simple linear model: y = Xw + b"""
    return X @ weights + bias


def sigmoid(z: np.ndarray) -> np.ndarray:
    """Sigmoid activation function"""
    return 1 / (1 + np.exp(-z))


def binary_cross_entropy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Binary cross-entropy loss"""
    epsilon = 1e-15
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))


def logistic_regression_train(X: np.ndarray, y: np.ndarray, 
                               learning_rate: float = 0.01, 
                               iterations: int = 100) -> Dict:
    """Train a logistic regression model"""
    m, n = X.shape
    weights = np.zeros(n)
    bias = 0
    losses = []
    
    for i in range(iterations):
        # Forward pass
        z = X @ weights + bias
        predictions = sigmoid(z)
        
        # Compute loss
        loss = binary_cross_entropy(y, predictions)
        losses.append(loss)
        
        # Backward pass (gradients)
        dz = predictions - y
        dw = (1/m) * (X.T @ dz)
        db = (1/m) * np.sum(dz)
        
        # Update parameters
        weights -= learning_rate * dw
        bias -= learning_rate * db
    
    return {
        'weights': weights.tolist(),
        'bias': float(bias),
        'final_loss': float(losses[-1]),
        'losses': losses
    }


def k_nearest_neighbors(X_train: np.ndarray, y_train: np.ndarray,
                        X_test: np.ndarray, k: int = 3) -> List:
    """K-Nearest Neighbors classifier"""
    predictions = []
    
    for test_point in X_test:
        # Calculate distances
        distances = np.sqrt(np.sum((X_train - test_point)**2, axis=1))
        
        # Get k nearest neighbors
        k_indices = np.argsort(distances)[:k]
        k_nearest_labels = y_train[k_indices]
        
        # Vote
        prediction = np.bincount(k_nearest_labels.astype(int)).argmax()
        predictions.append(prediction)
    
    return predictions


def pca_transform(X: np.ndarray, n_components: int = 2) -> Dict:
    """Principal Component Analysis"""
    # Center the data
    X_centered = X - np.mean(X, axis=0)
    
    # Covariance matrix
    cov_matrix = np.cov(X_centered.T)
    
    # Eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)


    eigenvalues = np.real(eigenvalues)
    eigenvectors = np.real(eigenvectors)
    
    # Sort by eigenvalues
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Select top n_components
    components = eigenvectors[:, :n_components]
    
    # Transform data
    X_transformed = X_centered @ components
    
    # Explained variance
    explained_variance = eigenvalues[:n_components] / np.sum(eigenvalues)
    
    return {
        'transformed_data': X_transformed.tolist(),
        'components': components.tolist(),
        'explained_variance': explained_variance.tolist(),
        'total_variance_explained': float(np.sum(explained_variance))
    }


def neural_network_forward(X: np.ndarray, 
                           W1: np.ndarray, b1: np.ndarray,
                           W2: np.ndarray, b2: np.ndarray) -> Dict:
    """Forward pass through a 2-layer neural network"""
    # Layer 1
    Z1 = X @ W1 + b1
    A1 = np.maximum(0, Z1)  # ReLU activation
    
    # Layer 2
    Z2 = A1 @ W2 + b2
    A2 = sigmoid(Z2)  # Sigmoid for output
    
    return {
        'output': A2.tolist(),
        'hidden_activation': A1.tolist(),
        'mean_output': float(np.mean(A2))
    }


def matrix_factorization(R: np.ndarray, k: int = 5, 
                        iterations: int = 100, 
                        learning_rate: float = 0.01) -> Dict:
    """Simple matrix factorization (like in recommender systems)"""
    m, n = R.shape
    
    # Initialize user and item matrices
    P = np.random.rand(m, k)
    Q = np.random.rand(n, k)
    
    errors = []
    
    for iteration in range(iterations):
        # Compute error
        R_hat = P @ Q.T
        error = np.sum((R - R_hat) ** 2)
        errors.append(error)
        
        # Update P and Q
        for i in range(m):
            for j in range(n):
                if R[i, j] > 0:  # Only for observed entries
                    error_ij = R[i, j] - np.dot(P[i, :], Q[j, :])
                    P[i, :] += learning_rate * error_ij * Q[j, :]
                    Q[j, :] += learning_rate * error_ij * P[i, :]
    
    return {
        'P': P.tolist(),
        'Q': Q.tolist(),
        'final_error': float(errors[-1]),
        'reconstruction': (P @ Q.T).tolist()
    }


def decision_boundary(X: np.ndarray, y: np.ndarray) -> Dict:
    """Calculate decision boundary for binary classification"""
    # Separate classes
    class_0 = X[y == 0]
    class_1 = X[y == 1]
    
    # Calculate centroids
    centroid_0 = np.mean(class_0, axis=0)
    centroid_1 = np.mean(class_1, axis=0)
    
    # Decision boundary (perpendicular bisector)
    midpoint = (centroid_0 + centroid_1) / 2
    direction = centroid_1 - centroid_0
    
    return {
        'centroid_class_0': centroid_0.tolist(),
        'centroid_class_1': centroid_1.tolist(),
        'midpoint': midpoint.tolist(),
        'direction_vector': direction.tolist(),
        'distance_between_centroids': float(np.linalg.norm(direction))
    }


def time_series_features(series: np.ndarray) -> Dict:
    """Extract features from time series"""
    return {
        'mean': float(np.mean(series)),
        'std': float(np.std(series)),
        'min': float(np.min(series)),
        'max': float(np.max(series)),
        'range': float(np.max(series) - np.min(series)),
        'median': float(np.median(series)),
        'variance': float(np.var(series)),
        'skewness': float(np.mean((series - np.mean(series))**3) / (np.std(series)**3)),
        'kurtosis': float(np.mean((series - np.mean(series))**4) / (np.std(series)**4))
    }


# Example usage functions
def demo_all_ml_functions():
    """Demonstrate all ML functions"""
    print("=== ML Functions Demo ===\n")
    
    # 1. Logistic Regression
    print("1. Logistic Regression")
    X = np.random.rand(100, 3)
    y = (X[:, 0] + X[:, 1] > 1).astype(int)
    result = logistic_regression_train(X, y, iterations=50)
    print(f"   Final Loss: {result['final_loss']:.4f}\n")
    
    # 2. KNN
    print("2. K-Nearest Neighbors")
    X_train = np.array([[1, 2], [2, 3], [3, 4], [6, 7], [7, 8], [8, 9]])
    y_train = np.array([0, 0, 0, 1, 1, 1])
    X_test = np.array([[2, 2], [7, 7]])
    predictions = k_nearest_neighbors(X_train, y_train, X_test, k=3)
    print(f"   Predictions: {predictions}\n")
    
    # 3. PCA
    print("3. Principal Component Analysis")
    X = np.random.rand(50, 5)
    pca_result = pca_transform(X, n_components=2)
    print(f"   Variance Explained: {pca_result['total_variance_explained']:.2%}\n")
    
    # 4. Time Series
    print("4. Time Series Features")
    series = np.random.randn(100).cumsum()
    ts_features = time_series_features(series)
    print(f"   Mean: {ts_features['mean']:.2f}, Std: {ts_features['std']:.2f}\n")
    
    print("=== Demo Complete! ===")


if __name__ == "__main__":
    demo_all_ml_functions()
