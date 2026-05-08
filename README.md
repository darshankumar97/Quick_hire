# Time Series Forecasting System

A production-ready end-to-end time series forecasting system for sales prediction using multiple machine learning models.

## Overview

This system implements a comprehensive forecasting pipeline that:
- Trains multiple forecasting models (SARIMA, Prophet, XGBoost, LSTM)
- Compares model performance using MAE, RMSE, and MAPE metrics
- Automatically selects the best model for each state
- Generates 8-week (56-day) forecasts for all US states
- Exposes predictions via a REST API

## Project Structure

```
forecasting-system/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # FastAPI endpoints
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── arima_model.py          # SARIMA implementation
│   │   ├── prophet_model.py        # Facebook Prophet implementation
│   │   ├── xgboost_model.py        # XGBoost with lag features
│   │   └── lstm_model.py           # Neural network (LSTM-inspired)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── preprocessing.py        # Data loading and cleaning
│   │   ├── feature_engineering.py  # Feature creation
│   │   ├── trainer.py              # Model training and evaluation
│   │   └── forecasting.py          # Forecast generation
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── metrics.py              # Evaluation metrics (MAE, RMSE, MAPE)
│   │
│   └── main.py                     # FastAPI application
│
├── notebooks/                      # Jupyter notebooks for exploration
│
├── saved_models/                   # Trained model files (auto-generated)
│
├── outputs/
│   ├── plots/                      # Visualization plots
│   ├── forecasts.csv              # Forecast results (CSV)
│   ├── forecasts.json             # Forecast results (JSON)
│   ├── model_metadata.json        # Model info
│   ├── summary.json               # Training summary
│   └── training.log               # Training logs
│
├── Forecasting Case- Study.xlsx   # Input data (must be in root)
│
├── requirements.txt                # Python dependencies
├── run_training.py                 # Main training script
├── README.md                        # This file
└── .gitignore                       # Git ignore rules
```

## Installation

### Prerequisites
- Python 3.9+
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd forecasting-system
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Excel file exists**
   - Ensure `Forecasting Case- Study.xlsx` is in the project root directory

## Quick Start

### Running the Training Pipeline

Execute the training script to train models and generate forecasts:

```bash
python run_training.py
```

This will:
1. Load data from the Excel file
2. Preprocess and handle missing dates/values
3. Train 4 models (SARIMA, Prophet, XGBoost, LSTM) for each state
4. Compare model performance using RMSE
5. Select the best model per state
6. Generate 56-day forecasts
7. Save results to `outputs/` directory

### Running the API Server

After training, start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

Access the interactive documentation at: `http://localhost:8000/docs`

## API Endpoints

### Health Check
```
GET /health
```
Returns API health status.

### Get Available States
```
GET /states
```
Returns list of all available states in the dataset.

### Get Forecast for a State
```
GET /forecast/{state}
```
Returns 8-week forecast for a specific state.

**Example:**
```
GET /forecast/California
```

**Response:**
```json
{
  "state": "California",
  "best_model": "Prophet",
  "forecast_horizon_days": 56,
  "forecast": [
    {
      "date": "2026-06-01",
      "predicted_sales": 450000000.5
    },
    {
      "date": "2026-06-02",
      "predicted_sales": 451000000.2
    }
  ]
}
```

### Get All Forecasts
```
GET /forecast-all
```
Returns forecasts for all states grouped by state.

### Get Model Information
```
GET /models
```
Returns information about trained models including model selection for each state.

**Response:**
```json
{
  "message": "Model information",
  "total_states": 50,
  "best_models": {
    "Alabama": "SARIMA",
    "California": "Prophet",
    "Texas": "XGBoost"
  },
  "model_count": {
    "SARIMA": 15,
    "Prophet": 18,
    "XGBoost": 12,
    "LSTM": 5
  }
}
```

### Retrain Models
```
POST /retrain
```
Retrains all models with the latest data. This is a synchronous operation and may take several minutes.

## Data Processing

### Preprocessing Steps

1. **Data Loading**: Reads Excel file with columns: State, Date, Total (sales), Category

2. **Column Normalization**: Converts all column names to lowercase

3. **Missing Date Handling**:
   - Detects missing dates in time series
   - Creates complete date range with daily frequency
   - Fills missing values using forward fill and backward fill

4. **Missing Value Handling**:
   - Forward fill for continuous imputation
   - Backward fill for initial periods
   - Removes remaining NaN values before training

### Feature Engineering

The system creates comprehensive features for machine learning models:

#### Lag Features
- `lag_1`: Previous day's sales
- `lag_7`: Sales from 7 days ago (weekly pattern)
- `lag_30`: Sales from 30 days ago (monthly pattern)

#### Rolling Statistics
- `rolling_mean_7`: 7-day rolling average
- `rolling_std_7`: 7-day rolling standard deviation

#### Date Features
- `day_of_week`: Day number (0-6)
- `month`: Month number (1-12)
- `week_of_year`: ISO week number
- `quarter`: Quarter (1-4)
- `day_of_year`: Day of year

#### Holiday Features
- `is_holiday`: Binary indicator for US holidays

## Forecasting Models

### 1. SARIMA (Seasonal ARIMA)
**What it is**: Statistical time series model capturing seasonality and trends

**Parameters**:
- Order: (1, 1, 1) - non-seasonal (p, d, q)
- Seasonal Order: (1, 1, 1, 12) - seasonal (P, D, Q, s)

**Best for**: Time series with strong seasonal patterns

**Advantages**:
- Interpretable coefficients
- Works well with seasonal data
- Low computational cost

### 2. Facebook Prophet
**What it is**: Additive decomposition model with trend and seasonality components

**Features**:
- Built-in handling of holidays
- Automatic changepoint detection
- Flexible seasonality

**Best for**: Business time series with weekly/yearly seasonality

**Advantages**:
- Robust to missing data
- Good for business forecasting
- Interpretable components

### 3. XGBoost with Feature Engineering
**What it is**: Gradient boosting model trained on engineered features

**Features Used**:
- Lag features (1, 7, 30 days)
- Rolling statistics (7-day window)
- Calendar features
- Holiday indicators

**Best for**: Complex non-linear relationships

**Advantages**:
- Captures non-linear patterns
- Feature importance insights
- High accuracy on complex data

### 4. LSTM (Neural Network)
**What it is**: Multi-layer perceptron with sequence learning capabilities

**Architecture**:
- Input: 30-day sequences
- Hidden layers: 64 → 32 units
- Output: Single value prediction
- Early stopping enabled

**Best for**: Long-range dependencies

**Advantages**:
- Captures temporal dependencies
- Flexible architecture
- Can learn complex patterns

## Evaluation Metrics

### MAE (Mean Absolute Error)
- Measures average absolute deviation from actual values
- Unit: Same as sales values
- Interpretation: Average prediction error in dollars

### RMSE (Root Mean Squared Error)
- Penalizes larger errors more heavily
- Unit: Same as sales values
- Primary metric for model selection

### MAPE (Mean Absolute Percentage Error)
- Measures percentage deviation
- Unit: Percentage (%)
- Interpretation: Average percentage error across all predictions

## Model Selection Process

1. **Data Split**: 80% training, 20% validation (chronological)
2. **Training**: Each model is trained on training data
3. **Validation**: Predictions are made on validation set
4. **Evaluation**: RMSE is calculated for each model
5. **Selection**: Model with lowest RMSE is selected
6. **Forecasting**: Best model generates 56-day future forecast

## Output Files

### forecasts.csv
CSV file with all forecasts:
- `date`: Forecast date
- `state`: State name
- `predicted_sales`: Predicted sales value
- `best_model`: Best model used for this state

### forecasts.json
JSON format of the same data for API consumption

### model_metadata.json
Metadata about the training run:
- Timestamp
- Forecast horizon
- Best models per state
- Number of states

### training.log
Complete training logs with detailed information

### summary.json
Training summary with success metrics

## Troubleshooting

### Excel File Not Found
- Ensure `Forecasting Case- Study.xlsx` is in the project root
- Check file name spelling and capitalization

### Import Errors
- Verify all packages installed: `pip install -r requirements.txt`
- Python version 3.9+

### Forecast Generation Fails
- Check data quality and date formats
- Ensure sufficient data points (minimum 60+ days recommended)
- Review training.log for detailed error messages

### API Port Already in Use
- Change port: `uvicorn app.main:app --port 8001 --reload`

## Performance Tips

1. **Data Quality**: Clean data improves forecast accuracy
2. **Data Volume**: More historical data (2+ years) improves models
3. **Regular Retraining**: Retrain monthly with new data
4. **Model Ensemble**: Consider averaging top 2-3 models
5. **Monitor RMSE**: Track validation RMSE over time

## Future Improvements

1. **Model Ensemble**: Combine predictions from multiple models
2. **Confidence Intervals**: Add prediction uncertainty quantification
3. **Automated Retraining**: Schedule periodic model updates
4. **Advanced Visualization**: Interactive dashboards
5. **Hyperparameter Tuning**: Automated parameter optimization
6. **Causal Models**: Incorporate external variables (price, promotions)
7. **Real-time Updates**: Streaming data support
8. **GPU Support**: Accelerated training with GPU
9. **Distributed Training**: Multi-state parallel processing
10. **Model Versioning**: Track model versions and performance

## Contributing

Guidelines for extending the system:

1. **New Models**: Implement model class in `app/models/` following existing pattern
2. **New Features**: Add feature functions in `app/services/feature_engineering.py`
3. **Metrics**: Add evaluation metrics in `app/utils/metrics.py`
4. **API Endpoints**: Add routes in `app/api/routes.py`

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review training logs in `outputs/training.log`
3. Check API documentation at `/docs` when server is running

## Technical Stack

- **Data Processing**: Pandas, NumPy
- **Forecasting Models**: statsmodels, Prophet, XGBoost, scikit-learn
- **API Framework**: FastAPI, Uvicorn
- **Visualization**: Matplotlib, Seaborn
- **Utilities**: holidays, joblib

## Performance Benchmarks

Typical execution times (50 states):
- Data preprocessing: 30 seconds
- Model training: 15-20 minutes
- Forecast generation: 2-3 minutes
- **Total**: ~20 minutes

Memory requirements:
- Minimum: 4GB RAM
- Recommended: 8GB+ RAM

## References

- [SARIMA Documentation](https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html)
- [Facebook Prophet](https://facebook.github.io/prophet/)
- [XGBoost Guide](https://xgboost.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
