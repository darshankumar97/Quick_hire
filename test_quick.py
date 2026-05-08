"""
Quick test script - trains on 2 states to verify system works
"""

import logging
import sys
from pathlib import Path
import pandas as pd

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.preprocessing import DataPreprocessor
from app.services.forecasting import ForecastingService

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting quick test training...")
    
    try:
        # Load data
        logger.info("Loading data...")
        preprocessor = DataPreprocessor('Forecasting Case- Study.xlsx')
        preprocessor.preprocess()
        
        # Get first 2 states
        states = preprocessor.get_all_states()[:2]
        logger.info(f"Testing with states: {states}")
        
        # Prepare state data
        state_data_dict = {}
        for state in states:
            state_data = preprocessor.get_state_data(state)
            state_data_dict[state] = state_data
            logger.info(f"  {state}: {len(state_data)} records")
        
        # Generate forecasts
        logger.info("Training models and generating forecasts...")
        forecasting_service = ForecastingService(forecast_horizon=56)
        result = forecasting_service.generate_all_forecasts(state_data_dict)
        
        logger.info(f"Success! Generated forecasts for {result['successful']} states")
        
        # Save outputs
        output_files = forecasting_service.save_forecasts()
        logger.info(f"Saved outputs: {list(output_files.values())}")
        
        # Show sample forecasts
        if 'all' in forecasting_service.state_forecasts:
            df = forecasting_service.state_forecasts['all']
            logger.info("\nSample forecasts:")
            for _, row in df.head().iterrows():
                logger.info(f"  {row['state']}: {row['date'].date()} = ${row['predicted_sales']:,.0f}")
        
        return 0
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
