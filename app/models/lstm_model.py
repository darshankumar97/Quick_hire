"""
Neural Network model for time series forecasting (LSTM-inspired)
Using sklearn neural networks as alternative to TensorFlow/PyTorch
"""

import numpy as np
import pandas as pd
import logging
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class LSTMModel:
    """
    LSTM-inspired neural network model using sklearn
    Creates sequences for time series prediction
    """
    
    def __init__(self, sequence_length: int = 30, hidden_units: int = 64,
                 learning_rate: float = 0.001, max_iterations: int = 500):
        """
        Initialize LSTM model
        
        Args:
            sequence_length: Length of input sequences
            hidden_units: Number of hidden units
            learning_rate: Learning rate
            max_iterations: Maximum iterations
        """
        self.sequence_length = sequence_length
        self.hidden_units = hidden_units
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        
        self.model = MLPRegressor(
            hidden_layer_sizes=(hidden_units, hidden_units // 2),
            learning_rate_init=learning_rate,
            max_iter=max_iterations,
            early_stopping=True,
            validation_fraction=0.1,
            random_state=42,
            verbose=False
        )
        self.scaler = StandardScaler()
        self.last_sequence = None
        
    def create_sequences(self, data: np.ndarray) -> tuple:
        """
        Create sequences for time series
        
        Args:
            data: 1D array of time series values
            
        Returns:
            Tuple of (X, y) sequences
        """
        X, y = [], []
        
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(data[i + self.sequence_length])
        
        return np.array(X), np.array(y)
    
    def fit(self, ts_data: np.ndarray) -> None:
        """
        Fit LSTM model
        
        Args:
            ts_data: 1D array of time series values
        """
        try:
            # Ensure data is 1D
            if ts_data.ndim > 1:
                ts_data = ts_data.flatten()
            
            # Create sequences
            X, y = self.create_sequences(ts_data)
            
            if len(X) == 0:
                logger.warning("Not enough data to create sequences")
                return
            
            # Reshape for MLP (flatten sequences)
            X_flat = X.reshape(X.shape[0], -1)
            
            # Scale data
            X_scaled = self.scaler.fit_transform(X_flat)
            
            # Fit model
            self.model.fit(X_scaled, y)
            
            # Store last sequence for forecasting
            self.last_sequence = X[-1]
            
            logger.info("LSTM model fitted successfully")
        except Exception as e:
            logger.error(f"Error fitting LSTM model: {str(e)}")
            raise
    
    def forecast(self, steps: int, historical_data: np.ndarray = None) -> np.ndarray:
        """
        Generate forecasts
        
        Args:
            steps: Number of steps to forecast
            historical_data: Historical data for context
            
        Returns:
            Forecast values
        """
        try:
            if self.last_sequence is None:
                raise ValueError("Model not fitted. Call fit() first.")
            
            forecasts = []
            current_sequence = self.last_sequence.copy()
            
            for _ in range(steps):
                # Reshape for prediction
                X_flat = current_sequence.reshape(1, -1)
                X_scaled = self.scaler.transform(X_flat)
                
                # Predict next value
                next_pred = self.model.predict(X_scaled)[0]
                forecasts.append(next_pred)
                
                # Update sequence (slide window)
                current_sequence = np.append(current_sequence[1:], next_pred)
            
            return np.array(forecasts)
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            raise
    
    def predict_in_sample(self, X: np.ndarray) -> np.ndarray:
        """Get in-sample predictions"""
        if X.ndim > 2:
            X = X.reshape(X.shape[0], -1)
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
