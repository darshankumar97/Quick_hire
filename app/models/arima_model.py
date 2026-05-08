"""
SARIMA forecasting model
"""

import pandas as pd
import numpy as np
import logging
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class SARIMAModel:
    """SARIMA model for time series forecasting"""
    
    def __init__(self, order: tuple = (1, 1, 1), seasonal_order: tuple = (1, 1, 1, 12)):
        """
        Initialize SARIMA model
        
        Args:
            order: ARIMA order (p, d, q)
            seasonal_order: Seasonal order (P, D, Q, s)
        """
        self.order = order
        self.seasonal_order = seasonal_order
        self.model = None
        self.results = None
        
    def fit(self, ts_data: pd.Series) -> None:
        """
        Fit SARIMA model
        
        Args:
            ts_data: Time series data
        """
        try:
            self.model = SARIMAX(
                ts_data,
                order=self.order,
                seasonal_order=self.seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            self.results = self.model.fit(disp=False)
            logger.info("SARIMA model fitted successfully")
        except Exception as e:
            logger.error(f"Error fitting SARIMA model: {str(e)}")
            raise
    
    def forecast(self, steps: int) -> np.ndarray:
        """
        Generate forecasts
        
        Args:
            steps: Number of steps to forecast
            
        Returns:
            Forecast values
        """
        try:
            forecast = self.results.get_forecast(steps=steps)
            return forecast.predicted_mean.values
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            raise
    
    def predict_in_sample(self) -> np.ndarray:
        """Get in-sample predictions"""
        return self.results.fittedvalues.values
