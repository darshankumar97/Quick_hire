"""
Facebook Prophet forecasting model
"""

import pandas as pd
import numpy as np
import logging
from prophet import Prophet
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class ProphetModel:
    """Facebook Prophet model for time series forecasting"""
    
    def __init__(self, yearly_seasonality: bool = True, weekly_seasonality: bool = True,
                 daily_seasonality: bool = False, changepoint_prior_scale: float = 0.05):
        """
        Initialize Prophet model
        
        Args:
            yearly_seasonality: Include yearly seasonality
            weekly_seasonality: Include weekly seasonality
            daily_seasonality: Include daily seasonality
            changepoint_prior_scale: Flexibility of trend
        """
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.daily_seasonality = daily_seasonality
        self.changepoint_prior_scale = changepoint_prior_scale
        self.model = None
        self.forecast = None
        
    def fit(self, df: pd.DataFrame) -> None:
        """
        Fit Prophet model
        
        Args:
            df: DataFrame with 'ds' (date) and 'y' (target) columns
        """
        try:
            self.model = Prophet(
                yearly_seasonality=self.yearly_seasonality,
                weekly_seasonality=self.weekly_seasonality,
                daily_seasonality=self.daily_seasonality,
                changepoint_prior_scale=self.changepoint_prior_scale,
                interval_width=0.95
            )
            
            # Add US holidays
            self.model.add_country_holidays('US')
            
            self.model.fit(df)
            logger.info("Prophet model fitted successfully")
        except Exception as e:
            logger.error(f"Error fitting Prophet model: {str(e)}")
            raise
    
    def forecast(self, periods: int) -> np.ndarray:
        """
        Generate forecasts
        
        Args:
            periods: Number of periods to forecast
            
        Returns:
            Forecast values
        """
        try:
            future = self.model.make_future_dataframe(periods=periods)
            forecast = self.model.predict(future)
            self.forecast = forecast
            
            # Return only the forecast part (not historical)
            return forecast['yhat'].tail(periods).values
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            raise
    
    def predict_in_sample(self) -> np.ndarray:
        """Get in-sample predictions"""
        if self.forecast is None:
            return np.array([])
        return self.forecast['yhat'].values
