"""
Model trainer and evaluator
"""

import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import joblib

from app.models.arima_model import SARIMAModel
from app.models.prophet_model import ProphetModel
from app.models.xgboost_model import XGBoostModel
from app.models.lstm_model import LSTMModel
from app.services.feature_engineering import FeatureEngineer
from app.utils.metrics import evaluate_model

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Trains and evaluates multiple forecasting models"""
    
    def __init__(self, forecast_horizon: int = 56):
        """
        Initialize trainer
        
        Args:
            forecast_horizon: Number of days to forecast (default 8 weeks = 56 days)
        """
        self.forecast_horizon = forecast_horizon
        self.models = {}
        self.results = {}
        self.best_model = None
        self.best_model_name = None
        self.models_dir = Path(__file__).parent.parent.parent / 'saved_models'
        self.models_dir.mkdir(exist_ok=True)
        
    def train_sarima(self, ts_data: pd.Series) -> dict:
        """Train SARIMA model"""
        logger.info("Training SARIMA model...")
        try:
            model = SARIMAModel()
            model.fit(ts_data)
            
            # Generate validation forecast
            validation_forecast = model.forecast(len(ts_data) // 4)
            
            self.models['SARIMA'] = model
            logger.info("SARIMA training complete")
            
            return {'status': 'success', 'model': model}
        except Exception as e:
            logger.error(f"SARIMA training failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def train_prophet(self, ts_data: pd.Series, dates: pd.Series) -> dict:
        """Train Prophet model"""
        logger.info("Training Prophet model...")
        try:
            # Prepare data in Prophet format
            df = pd.DataFrame({
                'ds': dates,
                'y': ts_data.values
            })
            df['ds'] = pd.to_datetime(df['ds'])
            
            model = ProphetModel()
            model.fit(df)
            
            self.models['Prophet'] = model
            logger.info("Prophet training complete")
            
            return {'status': 'success', 'model': model}
        except Exception as e:
            logger.error(f"Prophet training failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def train_xgboost(self, df: pd.DataFrame) -> dict:
        """Train XGBoost model"""
        logger.info("Training XGBoost model...")
        try:
            feature_engineer = FeatureEngineer()
            
            # Engineer features
            df_features = feature_engineer.engineer_features(df.copy())
            
            # Prepare ML features
            X, y, feature_names = feature_engineer.prepare_ml_features(df_features)
            
            if len(X) == 0:
                raise ValueError("No valid features generated for XGBoost")
            
            # Split into train/validation
            split_idx = int(len(X) * 0.8)
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Train model
            model = XGBoostModel()
            model.fit(X_train, y_train, feature_names)
            
            self.models['XGBoost'] = model
            logger.info("XGBoost training complete")
            
            return {'status': 'success', 'model': model}
        except Exception as e:
            logger.error(f"XGBoost training failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def train_lstm(self, ts_data: np.ndarray) -> dict:
        """Train LSTM model"""
        logger.info("Training LSTM model...")
        try:
            model = LSTMModel()
            model.fit(ts_data)
            
            self.models['LSTM'] = model
            logger.info("LSTM training complete")
            
            return {'status': 'success', 'model': model}
        except Exception as e:
            logger.error(f"LSTM training failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def train_all_models(self, state_data: pd.DataFrame) -> dict:
        """
        Train all models for a state
        
        Args:
            state_data: DataFrame with date, total columns
            
        Returns:
            Dictionary with training results
        """
        state_data = state_data.sort_values('date').reset_index(drop=True)
        
        logger.info(f"Training all models on {len(state_data)} data points...")
        
        results = {}
        
        # Train SARIMA
        results['SARIMA'] = self.train_sarima(pd.Series(state_data['total'].values))
        
        # Train Prophet
        results['Prophet'] = self.train_prophet(
            pd.Series(state_data['total'].values),
            pd.Series(state_data['date'].values)
        )
        
        # Train XGBoost
        results['XGBoost'] = self.train_xgboost(state_data)
        
        # Train LSTM
        results['LSTM'] = self.train_lstm(state_data['total'].values)
        
        return results
    
    def generate_all_forecasts(self) -> dict:
        """Generate forecasts from all trained models"""
        forecasts = {}
        
        for model_name, model in self.models.items():
            try:
                if model_name == 'SARIMA':
                    forecast = model.forecast(self.forecast_horizon)
                elif model_name == 'Prophet':
                    forecast = model.forecast(self.forecast_horizon)
                elif model_name == 'XGBoost':
                    # For XGBoost, we need features - use walk-forward approach
                    logger.info(f"Skipping walk-forward forecast for {model_name} in evaluation")
                    continue
                elif model_name == 'LSTM':
                    forecast = model.forecast(self.forecast_horizon)
                
                forecasts[model_name] = forecast
            except Exception as e:
                logger.error(f"Error generating forecast for {model_name}: {str(e)}")
        
        return forecasts
    
    def select_best_model(self, y_val: np.ndarray, forecasts: dict) -> tuple:
        """
        Select best model based on validation RMSE
        
        Args:
            y_val: Validation data
            forecasts: Dictionary of forecasts from each model
            
        Returns:
            Tuple of (best_model_name, best_metrics)
        """
        model_scores = {}
        
        for model_name, forecast in forecasts.items():
            if len(forecast) != len(y_val):
                continue
            
            metrics = evaluate_model(y_val, forecast)
            model_scores[model_name] = metrics
            
            logger.info(f"{model_name} - RMSE: {metrics['RMSE']:.2f}, MAE: {metrics['MAE']:.2f}, MAPE: {metrics['MAPE']:.2f}%")
        
        if not model_scores:
            logger.warning("No valid models for comparison")
            return None, None
        
        # Select based on RMSE
        best_model = min(model_scores.items(), key=lambda x: x[1]['RMSE'])
        
        self.best_model_name = best_model[0]
        self.best_model = self.models[best_model[0]]
        
        logger.info(f"\nBest model: {best_model[0]}")
        logger.info(f"Best RMSE: {best_model[1]['RMSE']:.2f}")
        
        return best_model[0], {**best_model[1], 'model_name': best_model[0], 'all_models': model_scores}
    
    def save_models(self, state: str) -> None:
        """Save trained models to disk"""
        try:
            for model_name, model in self.models.items():
                filepath = self.models_dir / f"{state}_{model_name.lower()}.pkl"
                joblib.dump(model, filepath)
                logger.info(f"Saved {model_name} model for {state}")
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
    
    def load_models(self, state: str) -> None:
        """Load trained models from disk"""
        try:
            for model_file in self.models_dir.glob(f"{state}_*.pkl"):
                model_name = model_file.stem.replace(f"{state}_", "").upper()
                model = joblib.load(model_file)
                self.models[model_name] = model
                logger.info(f"Loaded {model_name} model for {state}")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
