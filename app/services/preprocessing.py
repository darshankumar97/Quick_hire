"""
Data preprocessing module for time series forecasting
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Handles data loading, cleaning, and preparation"""
    
    def __init__(self, excel_file_path: str):
        """Initialize preprocessor with Excel file path"""
        self.excel_file_path = excel_file_path
        self.raw_data = None
        self.processed_data = None
        
    def load_data(self) -> pd.DataFrame:
        """Load data from Excel file"""
        try:
            df = pd.read_excel(self.excel_file_path)
            logger.info(f"Data loaded successfully. Shape: {df.shape}")
            logger.info(f"Columns: {df.columns.tolist()}")
            self.raw_data = df
            return df
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to lowercase"""
        df.columns = df.columns.str.lower().str.strip()
        return df
    
    def handle_missing_dates(self, df: pd.DataFrame, state: str) -> pd.DataFrame:
        """
        Fill missing dates for a state with daily frequency
        Uses forward fill for missing values
        """
        # Filter data for specific state
        state_data = df[df['state'] == state].copy()
        
        # Convert date column to datetime
        state_data['date'] = pd.to_datetime(state_data['date'])
        
        # Create a complete date range
        date_range = pd.date_range(
            start=state_data['date'].min(),
            end=state_data['date'].max(),
            freq='D'
        )
        
        # Create a complete dataframe for all dates
        complete_df = pd.DataFrame({'date': date_range})
        state_data = state_data.set_index('date').reindex(complete_df['date']).reset_index()
        state_data.columns = ['date', 'state', 'total', 'category']
        
        # Forward fill missing values
        state_data['total'] = state_data['total'].fillna(method='ffill')
        state_data['state'] = state
        state_data['category'] = state_data['category'].fillna(method='ffill')
        
        # Backward fill if needed (for dates before first value)
        state_data['total'] = state_data['total'].fillna(method='bfill')
        state_data['category'] = state_data['category'].fillna(method='bfill')
        
        return state_data
    
    def preprocess(self) -> pd.DataFrame:
        """Complete preprocessing pipeline"""
        if self.raw_data is None:
            self.load_data()
        
        df = self.raw_data.copy()
        
        # Normalize column names
        df = self.normalize_columns(df)
        
        logger.info("Processing data for each state...")
        
        # Process each state
        states = df['state'].unique()
        processed_states = []
        
        for state in states:
            try:
                state_data = self.handle_missing_dates(df, state)
                processed_states.append(state_data)
            except Exception as e:
                logger.warning(f"Error processing state {state}: {str(e)}")
                continue
        
        self.processed_data = pd.concat(processed_states, ignore_index=True)
        
        logger.info(f"Preprocessing complete. Processed data shape: {self.processed_data.shape}")
        
        return self.processed_data
    
    def get_state_data(self, state: str) -> pd.DataFrame:
        """Get preprocessed data for a specific state"""
        if self.processed_data is None:
            self.preprocess()
        
        state_data = self.processed_data[self.processed_data['state'] == state].copy()
        state_data = state_data.sort_values('date').reset_index(drop=True)
        
        return state_data
    
    def get_all_states(self) -> list:
        """Get list of all states in the data"""
        if self.processed_data is None:
            self.preprocess()
        
        return self.processed_data['state'].unique().tolist()
