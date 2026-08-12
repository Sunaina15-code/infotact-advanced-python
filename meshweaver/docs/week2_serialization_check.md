# Week 2: Serialization Check

## Overview
Test transmitting and executing complex ML/Math functions across the network.

## Objectives
1. ✅ Serialize complex mathematical functions
2. ✅ Serialize ML/AI algorithms (regression, classification, clustering)
3. ✅ Transmit serialized functions across simulated network
4. ✅ Execute transmitted functions on remote nodes
5. ✅ Validate results match local execution

## Test Categories

### 1. Basic Serialization Tests (`test_serialization.py`)
- Simple math functions
- Lambda functions
- Functions with closures
- NumPy array operations
- Complex statistical computations

### 2. ML Function Tests (`test_ml_functions.py`)
- Linear Regression
- K-Means Clustering
- Neural Network Activations
- Gradient Descent
- Decision Tree Logic
- Feature Engineering Pipelines

### 3. Network Transmission Tests (`test_network_transmission.py`)
- Simulated network transmission
- Multi-node task distribution
- Large data serialization
- Functions with external dependencies
- Error handling
- Concurrent execution

## Running Tests

```bash
# Run all Week 2 tests
cd meshweaver/tests
python -m unittest discover -v

# Run specific test suite
python test_serialization.py
python test_ml_functions.py
python test_network_transmission.py

# Run complete demo
cd meshweaver/tests
python ml_network_transmission_demo.py
