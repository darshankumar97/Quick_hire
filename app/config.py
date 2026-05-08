"""
Configuration constants for the forecasting system
"""

# Data Configuration
FORECAST_HORIZON = 56  # days (8 weeks)
TRAIN_TEST_SPLIT = 0.8  # 80% training, 20% validation
MISSING_DATE_FILL_METHOD = 'ffill'  # Forward fill for missing dates

# Excel File
EXCEL_FILE_NAME = 'Forecasting Case- Study.xlsx'
REQUIRED_COLUMNS = ['State', 'Date', 'Total', 'Category']

# Feature Engineering
LAG_PERIODS = [1, 7, 30]
ROLLING_WINDOW = 7
HOLIDAY_COUNTRY = 'US'

# SARIMA Configuration
SARIMA_ORDER = (1, 1, 1)  # (p, d, q)
SARIMA_SEASONAL_ORDER = (1, 1, 1, 12)  # (P, D, Q, s)

# Prophet Configuration
PROPHET_YEARLY_SEASONALITY = True
PROPHET_WEEKLY_SEASONALITY = True
PROPHET_DAILY_SEASONALITY = False
PROPHET_CHANGEPOINT_PRIOR_SCALE = 0.05

# XGBoost Configuration
XGBOOST_N_ESTIMATORS = 100
XGBOOST_MAX_DEPTH = 6
XGBOOST_LEARNING_RATE = 0.1
XGBOOST_RANDOM_STATE = 42

# LSTM Configuration
LSTM_SEQUENCE_LENGTH = 30
LSTM_HIDDEN_UNITS = 64
LSTM_LEARNING_RATE = 0.001
LSTM_MAX_ITERATIONS = 500

# Evaluation Metrics
EVALUATION_METRICS = ['MAE', 'RMSE', 'MAPE']
BEST_MODEL_METRIC = 'RMSE'  # Lower is better

# Paths
PROJECT_ROOT = '.'
OUTPUT_DIR = './outputs'
SAVED_MODELS_DIR = './saved_models'
PLOTS_DIR = './outputs/plots'
LOG_FILE = './outputs/training.log'

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# API Configuration
API_HOST = '0.0.0.0'
API_PORT = 8000
API_RELOAD = True
API_TITLE = 'Time Series Forecasting API'
API_VERSION = '1.0.0'

# Data Constraints
MIN_RECORDS_PER_STATE = 60  # Minimum data points needed
MIN_FORECAST_ACCURACY = 0.0  # No minimum accuracy requirement

# Feature Names
FEATURE_COLUMNS = [
    'lag_1', 'lag_7', 'lag_30',
    'rolling_mean_7', 'rolling_std_7',
    'day_of_week', 'month', 'week_of_year', 'quarter', 'day_of_year',
    'is_holiday'
]
