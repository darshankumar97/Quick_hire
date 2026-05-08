"""
FastAPI endpoints for forecasting API
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging
import pandas as pd
from pathlib import Path

from app.services.preprocessing import DataPreprocessor
from app.services.forecasting import ForecastingService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global service instances
preprocessor = None
forecasting_service = None
forecasts_data = None


def load_forecasts_from_csv():
    """Load pre-generated forecasts from CSV file"""
    try:
        outputs_dir = Path(__file__).parent.parent.parent / 'outputs'
        csv_file = outputs_dir / 'forecasts.csv'
        
        if csv_file.exists():
            logger.info(f"Loading forecasts from {csv_file}")
            df = pd.read_csv(csv_file)
            df['date'] = pd.to_datetime(df['date'])
            
            # Group by state
            forecasts_by_state = {}
            for state in df['state'].unique():
                state_df = df[df['state'] == state].copy()
                forecasts_by_state[state] = state_df
            
            return forecasts_by_state
        else:
            logger.warning(f"Forecasts CSV not found at {csv_file}")
            return {}
    except Exception as e:
        logger.error(f"Error loading forecasts from CSV: {e}")
        return {}


def initialize_services(excel_file: str = None):
    """Initialize services"""
    global preprocessor, forecasting_service, forecasts_data
    
    try:
        if excel_file:
            preprocessor = DataPreprocessor(excel_file)
        else:
            preprocessor = None
            
        forecasting_service = ForecastingService(forecast_horizon=56)
        
        # Load pre-generated forecasts from CSV
        forecasts_data = load_forecasts_from_csv()
        
        if forecasts_data:
            logger.info(f"Loaded forecasts for {len(forecasts_data)} states")
            # Store in forecasting service
            for state, df in forecasts_data.items():
                forecasting_service.state_forecasts[state] = df
                if not df.empty:
                    best_model = df['best_model'].iloc[0]
                    forecasting_service.state_best_models[state] = best_model
        else:
            logger.warning("No pre-generated forecasts found")
            
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise


@router.get("/health", tags=["Health"])
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "message": "Time Series Forecasting API is running"
    }


@router.get("/models", tags=["Models"])
async def get_models():
    """Get information about trained models"""
    try:
        if forecasting_service is None:
            raise HTTPException(status_code=400, detail="Services not initialized")
        
        best_models = forecasting_service.state_best_models
        
        if not best_models:
            return {
                "message": "No models trained yet",
                "total_states": 0,
                "models": {}
            }
        
        return {
            "message": "Model information",
            "total_states": len(best_models),
            "best_models": best_models,
            "model_count": {
                "SARIMA": sum(1 for v in best_models.values() if v == "SARIMA"),
                "Prophet": sum(1 for v in best_models.values() if v == "Prophet"),
                "XGBoost": sum(1 for v in best_models.values() if v == "XGBoost"),
                "LSTM": sum(1 for v in best_models.values() if v == "LSTM")
            }
        }
    except Exception as e:
        logger.error(f"Error in get_models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/{state}", tags=["Forecasting"])
async def get_forecast(state: str):
    """
    Get 8-week forecast for a specific state
    
    Args:
        state: State name (e.g., 'California', 'Texas')
        
    Returns:
        Forecast data with dates and predicted sales
    """
    try:
        if forecasting_service is None:
            raise HTTPException(status_code=400, detail="Services not initialized")
        
        if state not in forecasting_service.state_forecasts:
            raise HTTPException(status_code=404, detail=f"No forecast found for {state}")
        
        forecast_df = forecasting_service.state_forecasts[state]
        best_model = forecasting_service.state_best_models.get(state, "Unknown")
        
        # Convert to JSON format
        forecast_list = []
        for _, row in forecast_df.iterrows():
            date_val = row['date']
            if not isinstance(date_val, str):
                date_val = pd.Timestamp(date_val).strftime('%Y-%m-%d')
            
            forecast_list.append({
                "date": date_val,
                "predicted_sales": float(row['predicted_sales'])
            })
        
        return {
            "state": state,
            "best_model": best_model,
            "forecast_horizon_days": len(forecast_list),
            "forecast": forecast_list
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting forecast for {state}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/states", tags=["Data"])
async def get_states():
    """Get list of all available states"""
    try:
        states = []
        
        # Try to get states from forecasts first (most reliable)
        if forecasting_service and forecasting_service.state_forecasts:
            states = list(forecasting_service.state_forecasts.keys())
        
        # Fallback to preprocessor
        if not states and preprocessor:
            states = preprocessor.get_all_states()
        
        if not states:
            return {
                "total_states": 0,
                "states": [],
                "message": "No states found"
            }
        
        return {
            "total_states": len(states),
            "states": sorted(states)
        }
    except Exception as e:
        logger.error(f"Error getting states: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrain", tags=["Training"])
async def retrain_models():
    """Retrain all models with latest data"""
    try:
        if preprocessor is None or forecasting_service is None:
            raise HTTPException(status_code=400, detail="Services not initialized")
        
        # Load and preprocess data
        logger.info("Starting model retraining...")
        preprocessor.preprocess()
        
        # Prepare state data
        states = preprocessor.get_all_states()
        state_data_dict = {}
        
        for state in states:
            state_data_dict[state] = preprocessor.get_state_data(state)
        
        # Generate forecasts
        result = forecasting_service.generate_all_forecasts(state_data_dict)
        
        # Save outputs
        output_files = forecasting_service.save_forecasts()
        forecasting_service.save_model_metadata()
        
        return {
            "status": "success",
            "message": "Models retrained successfully",
            "total_states": result['total_states'],
            "successful_states": result['successful'],
            "output_files": output_files
        }
    except Exception as e:
        logger.error(f"Error during retraining: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast-all", tags=["Forecasting"])
async def get_all_forecasts():
    """Get forecasts for all states"""
    try:
        if forecasting_service is None:
            raise HTTPException(status_code=400, detail="Services not initialized")
        
        if 'all' not in forecasting_service.state_forecasts:
            raise HTTPException(status_code=404, detail="No combined forecasts available")
        
        forecast_df = forecasting_service.state_forecasts['all']
        
        # Group by state
        forecasts_by_state = {}
        for state in forecast_df['state'].unique():
            state_forecast = forecast_df[forecast_df['state'] == state]
            forecasts_by_state[state] = [
                {
                    "date": row['date'].strftime('%Y-%m-%d'),
                    "predicted_sales": float(row['predicted_sales']),
                    "best_model": row.get('best_model', 'Unknown')
                }
                for _, row in state_forecast.iterrows()
            ]
        
        return {
            "total_states": len(forecasts_by_state),
            "forecast_horizon_days": len(forecasts_by_state[list(forecasts_by_state.keys())[0]]) if forecasts_by_state else 0,
            "forecasts": forecasts_by_state
        }
    except Exception as e:
        logger.error(f"Error getting all forecasts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
