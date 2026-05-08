"""
Feature engineering for time series forecasting
"""

import pandas as pd
import numpy as np
import logging
import holidays

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Handles feature engineering for machine learning models"""
    
    def __init__(self):
        """Initialize feature engineer"""
        self.us_holidays = holidays.US()
    
    def create_lag_features(self, df: pd.DataFrame, lags: list = [1, 7, 30]) -> pd.DataFrame:
        """
        Create lag features for time series
        
        Args:
            df: DataFrame with 'total' column
            lags: List of lag periods
            
        Returns:
            DataFrame with lag features
        """
        df = df.copy()
        for lag in lags:
            df[f'lag_{lag}'] = df['total'].shift(lag)
        
        return df
    
    def create_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create rolling statistics features
        
        Args:
            df: DataFrame with 'total' column
            
        Returns:
            DataFrame with rolling features
        """
        df = df.copy()
        
        # 7-day rolling mean and std
        df['rolling_mean_7'] = df['total'].rolling(window=7, min_periods=1).mean()
        df['rolling_std_7'] = df['total'].rolling(window=7, min_periods=1).std()
        df['rolling_std_7'] = df['rolling_std_7'].fillna(0)
        
        return df
    
    def create_date_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create date-based features
        
        Args:
            df: DataFrame with 'date' column
            
        Returns:
            DataFrame with date features
        """
        df = df.copy()
        
        # Ensure date column is datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract date features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['quarter'] = df['date'].dt.quarter
        df['day_of_year'] = df['date'].dt.dayofyear
        
        return df
    
    def create_holiday_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create holiday indicator features (US holidays)
        
        Args:
            df: DataFrame with 'date' column
            
        Returns:
            DataFrame with holiday feature
        """
        df = df.copy()
        
        # Ensure date column is datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Create holiday indicator
        df['is_holiday'] = df['date'].apply(lambda x: 1 if x in self.us_holidays else 0)
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Complete feature engineering pipeline
        
        Args:
            df: Input DataFrame with 'date' and 'total' columns
            
        Returns:
            DataFrame with all engineered features
        """
        logger.info("Starting feature engineering...")
        
        df = df.copy()
        
        # Create all features
        df = self.create_lag_features(df)
        df = self.create_rolling_features(df)
        df = self.create_date_features(df)
        df = self.create_holiday_features(df)
        
        logger.info(f"Feature engineering complete. Total features: {df.shape[1]}")
        
        return df
    
    def prepare_ml_features(self, df: pd.DataFrame) -> tuple:
        """
        Prepare features for ML models (XGBoost, etc.)
        
        Args:
            df: DataFrame with engineered features
            
        Returns:
            Tuple of (X, y) where X is features and y is target
        """
        df = df.copy()
        
        # Drop rows with NaN values
        df = df.dropna()
        
        # Define feature columns
        feature_cols = [col for col in df.columns if col not in ['date', 'state', 'total', 'category']]
        
        X = df[feature_cols].values
        y = df['total'].values
        
        logger.info(f"ML features prepared. Shape: X={X.shape}, y={y.shape}")
        
        return X, y, feature_cols
