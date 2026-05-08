"""
XGBoost forecasting model with engineered features
"""

import numpy as np
import pandas as pd
import logging
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class XGBoostModel:
    """XGBoost model for time series forecasting"""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 6,
                 learning_rate: float = 0.1, random_state: int = 42):
        """
        Initialize XGBoost model
        
        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate
            random_state: Random seed
        """
        self.model = XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
            verbosity=0
        )
        self.scaler = StandardScaler()
        self.feature_names = None
        
    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: list = None) -> None:
        """
        Fit XGBoost model
        
        Args:
            X: Feature matrix
            y: Target values
            feature_names: List of feature names
        """
        try:
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            self.model.fit(X_scaled, y, verbose=False)
            self.feature_names = feature_names
            
            logger.info("XGBoost model fitted successfully")
        except Exception as e:
            logger.error(f"Error fitting XGBoost model: {str(e)}")
            raise
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Generate predictions
        
        Args:
            X: Feature matrix
            
        Returns:
            Predictions
        """
        try:
            X_scaled = self.scaler.transform(X)
            return self.model.predict(X_scaled)
        except Exception as e:
            logger.error(f"Error generating predictions: {str(e)}")
            raise
    
    def get_feature_importance(self) -> dict:
        """Get feature importance scores"""
        if self.feature_names is None:
            return {}
        
        importance = dict(zip(self.feature_names, self.model.feature_importances_))
        return sorted(importance.items(), key=lambda x: x[1], reverse=True)
