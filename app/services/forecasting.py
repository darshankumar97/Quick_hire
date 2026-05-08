"""
Forecasting service - handles prediction generation and storage
"""

import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import joblib

from app.services.trainer import ModelTrainer
from app.utils.metrics import evaluate_model

logger = logging.getLogger(__name__)


class ForecastingService:
    """Handles forecasting for all states"""
    
    def __init__(self, forecast_horizon: int = 56):
        """
        Initialize forecasting service
        
        Args:
            forecast_horizon: Number of days to forecast
        """
        self.forecast_horizon = forecast_horizon
        self.state_models = {}
        self.state_forecasts = {}
        self.state_best_models = {}
        self.outputs_dir = Path(__file__).parent.parent.parent / 'outputs'
        self.outputs_dir.mkdir(exist_ok=True)
        
    def generate_forecast_dates(self, last_date: pd.Timestamp) -> list:
        """Generate future forecast dates"""
        dates = []
        current_date = last_date + timedelta(days=1)
        
        for _ in range(self.forecast_horizon):
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        return dates
    
    def forecast_for_state(self, state: str, state_data: pd.DataFrame) -> dict:
        """
        Generate forecasts for a specific state
        
        Args:
            state: State name
            state_data: DataFrame with 'date' and 'total' columns
            
        Returns:
            Dictionary with forecast and model info
        """
        logger.info(f"Generating forecast for {state}...")
        
        try:
            # Sort data
            state_data = state_data.sort_values('date').reset_index(drop=True)
            
            # Split data (80-20 train-validation)
            split_idx = int(len(state_data) * 0.8)
            train_data = state_data[:split_idx]
            val_data = state_data[split_idx:]
            
            # Train models
            trainer = ModelTrainer(self.forecast_horizon)
            trainer.train_all_models(train_data)
            
            # Generate forecasts
            forecasts = {}
            
            # SARIMA
            try:
                sarima_model = trainer.models['SARIMA']
                forecasts['SARIMA'] = sarima_model.forecast(len(val_data))
            except:
                pass
            
            # Prophet
            try:
                prophet_model = trainer.models['Prophet']
                forecasts['Prophet'] = prophet_model.forecast(len(val_data))
            except:
                pass
            
            # LSTM
            try:
                lstm_model = trainer.models['LSTM']
                forecasts['LSTM'] = lstm_model.forecast(len(val_data))
            except:
                pass
            
            # Evaluate and select best
            val_values = val_data['total'].values
            best_model, metrics = trainer.select_best_model(val_values, forecasts)
            
            # Store results
            self.state_models[state] = trainer.models
            self.state_best_models[state] = best_model
            
            # Generate future forecast using best model
            full_data = state_data['total'].values
            future_forecast = None
            
            if best_model == 'SARIMA':
                try:
                    model = trainer.models['SARIMA']
                    future_forecast = model.forecast(self.forecast_horizon)
                except:
                    pass
            elif best_model == 'Prophet':
                try:
                    model = trainer.models['Prophet']
                    future_forecast = model.forecast(self.forecast_horizon)
                except:
                    pass
            elif best_model == 'LSTM':
                try:
                    model = trainer.models['LSTM']
                    future_forecast = model.forecast(self.forecast_horizon)
                except:
                    pass
            
            # If best model fails, use SARIMA fallback
            if future_forecast is None:
                try:
                    model = trainer.models['SARIMA']
                    future_forecast = model.forecast(self.forecast_horizon)
                except:
                    future_forecast = np.full(self.forecast_horizon, np.mean(full_data))
            
            # Generate forecast dates
            last_date = pd.to_datetime(state_data['date'].iloc[-1])
            forecast_dates = self.generate_forecast_dates(last_date)
            
            # Create forecast dataframe
            forecast_df = pd.DataFrame({
                'date': forecast_dates,
                'predicted_sales': future_forecast,
                'state': state,
                'best_model': best_model
            })
            
            self.state_forecasts[state] = forecast_df
            
            logger.info(f"Forecast for {state} generated using {best_model}")
            
            return {
                'state': state,
                'best_model': best_model,
                'metrics': metrics,
                'forecast_df': forecast_df,
                'num_forecast_points': len(future_forecast)
            }
            
        except Exception as e:
            logger.error(f"Error forecasting for {state}: {str(e)}")
            return {
                'state': state,
                'error': str(e)
            }
    
    def generate_all_forecasts(self, preprocessor_data: dict) -> dict:
        """
        Generate forecasts for all states
        
        Args:
            preprocessor_data: Dictionary with state-wise data from preprocessor
            
        Returns:
            Dictionary with all forecasts and results
        """
        logger.info("Generating forecasts for all states...")
        
        all_results = []
        all_forecasts = []
        
        for state, state_data in preprocessor_data.items():
            result = self.forecast_for_state(state, state_data)
            all_results.append(result)
            
            if 'forecast_df' in result:
                all_forecasts.append(result['forecast_df'])
        
        # Combine all forecasts
        if all_forecasts:
            combined_forecasts = pd.concat(all_forecasts, ignore_index=True)
            self.state_forecasts['all'] = combined_forecasts
        
        return {
            'results': all_results,
            'total_states': len(preprocessor_data),
            'successful': sum(1 for r in all_results if 'forecast_df' in r)
        }
    
    def save_forecasts(self) -> dict:
        """Save forecasts to CSV and JSON"""
        try:
            output_files = {}
            
            # Save combined forecasts
            if 'all' in self.state_forecasts:
                df = self.state_forecasts['all']
                
                # CSV
                csv_path = self.outputs_dir / 'forecasts.csv'
                df.to_csv(csv_path, index=False)
                output_files['csv'] = str(csv_path)
                logger.info(f"Forecasts saved to {csv_path}")
                
                # JSON
                json_data = []
                for _, row in df.iterrows():
                    json_data.append({
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'state': row['state'],
                        'predicted_sales': float(row['predicted_sales']),
                        'best_model': row['best_model']
                    })
                
                json_path = self.outputs_dir / 'forecasts.json'
                with open(json_path, 'w') as f:
                    json.dump(json_data, f, indent=2)
                output_files['json'] = str(json_path)
                logger.info(f"Forecasts saved to {json_path}")
            
            return output_files
            
        except Exception as e:
            logger.error(f"Error saving forecasts: {str(e)}")
            return {}
    
    def save_model_metadata(self) -> None:
        """Save metadata about selected best models"""
        try:
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'forecast_horizon': self.forecast_horizon,
                'best_models': self.state_best_models,
                'num_states': len(self.state_best_models)
            }
            
            metadata_path = self.outputs_dir / 'model_metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Model metadata saved to {metadata_path}")
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
