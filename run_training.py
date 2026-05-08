"""
Main training script - run forecasting for all states
"""

import logging
import sys
from pathlib import Path
import pandas as pd
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.preprocessing import DataPreprocessor
from app.services.forecasting import ForecastingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'outputs' / 'training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def find_excel_file():
    """Find Excel file in project root"""
    for file in project_root.glob("*.xlsx"):
        logger.info(f"Found Excel file: {file}")
        return str(file)
    
    raise FileNotFoundError("No Excel file found in project root")


def main():
    """Main training pipeline"""
    logger.info("=" * 80)
    logger.info("Time Series Forecasting System - Training Pipeline")
    logger.info("=" * 80)
    
    try:
        # Find and load data
        logger.info("\n[1/4] Loading data...")
        excel_file = find_excel_file()
        
        preprocessor = DataPreprocessor(excel_file)
        raw_data = preprocessor.load_data()
        logger.info(f"Raw data shape: {raw_data.shape}")
        
        # Preprocess data
        logger.info("\n[2/4] Preprocessing data...")
        preprocessed_data = preprocessor.preprocess()
        logger.info(f"Preprocessed data shape: {preprocessed_data.shape}")
        
        # Get all states
        states = preprocessor.get_all_states()
        logger.info(f"Total states: {len(states)}")
        logger.info(f"States: {', '.join(sorted(states)[:5])}... and more")
        
        # Prepare state data
        logger.info("\n[3/4] Preparing state data...")
        state_data_dict = {}
        for state in states:
            state_data = preprocessor.get_state_data(state)
            state_data_dict[state] = state_data
            logger.info(f"  {state}: {len(state_data)} records")
        
        # Generate forecasts
        logger.info("\n[4/4] Generating forecasts...")
        forecasting_service = ForecastingService(forecast_horizon=56)
        
        result = forecasting_service.generate_all_forecasts(state_data_dict)
        logger.info(f"Successfully generated forecasts for {result['successful']} out of {result['total_states']} states")
        
        # Save outputs
        logger.info("\nSaving outputs...")
        output_files = forecasting_service.save_forecasts()
        forecasting_service.save_model_metadata()
        
        logger.info("Output files:")
        for file_type, filepath in output_files.items():
            logger.info(f"  {file_type}: {filepath}")
        
        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("Training Complete!")
        logger.info("=" * 80)
        
        if 'all' in forecasting_service.state_forecasts:
            forecast_df = forecasting_service.state_forecasts['all']
            logger.info(f"Total forecast points: {len(forecast_df)}")
            logger.info(f"Date range: {forecast_df['date'].min()} to {forecast_df['date'].max()}")
            
            # Show sample
            logger.info("\nSample forecasts (first 5 points, all states):")
            sample = forecast_df.head(len(states))
            for _, row in sample.iterrows():
                logger.info(f"  {row['state']:15s} - {row['date'].date()}: ${row['predicted_sales']:,.0f} (Model: {row['best_model']})")
        
        # Save summary
        summary = {
            'status': 'success',
            'total_states': result['total_states'],
            'successful_states': result['successful'],
            'forecast_horizon_days': 56,
            'output_files': output_files,
            'best_models': forecasting_service.state_best_models
        }
        
        summary_file = project_root / 'outputs' / 'summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"\nSummary saved to {summary_file}")
        
        logger.info("\nNext steps:")
        logger.info("1. Review forecasts in outputs/forecasts.csv")
        logger.info("2. Start API server: uvicorn app.main:app --reload")
        logger.info("3. Access API at http://localhost:8000/docs")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
