"""
Evaluation metrics for time series forecasting models
"""

import numpy as np
from typing import Dict, Tuple


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate Mean Absolute Error"""
    return np.mean(np.abs(y_true - y_pred))


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate Root Mean Squared Error"""
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate Mean Absolute Percentage Error"""
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate all evaluation metrics
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
        
    Returns:
        Dictionary with MAE, RMSE, MAPE
    """
    return {
        'MAE': calculate_mae(y_true, y_pred),
        'RMSE': calculate_rmse(y_true, y_pred),
        'MAPE': calculate_mape(y_true, y_pred)
    }
