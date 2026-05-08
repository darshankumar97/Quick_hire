# Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Python 3.9+
- 4GB+ RAM

### Step 1: Install Dependencies (2 minutes)
```bash
cd forecasting-system
pip install -r requirements.txt
```

### Step 2: Run Training (varies based on data size)
```bash
python run_training.py
```

This will:
- Load data from `Forecasting Case- Study.xlsx`
- Train 4 models for each state (SARIMA, Prophet, XGBoost, LSTM)
- Generate 56-day forecasts
- Save results to `outputs/`

### Step 3: Start API (1 minute)
```bash
uvicorn app.main:app --reload
```

API will be running at: `http://localhost:8000`

### Step 4: Test API (1 minute)
```bash
python example_api_client.py
```

Or open browser to: `http://localhost:8000/docs`

---

## Common Commands

```bash
# Test quick (2 states only)
python test_quick.py

# Full training
python run_training.py

# Start API server
uvicorn app.main:app --reload

# Run API client example
python example_api_client.py

# View logs
cat outputs/training.log

# View generated forecasts
cat outputs/forecasts.csv
```

---

## Output Files

After training, you'll find:

- **outputs/forecasts.csv** - All forecasts in CSV format
- **outputs/forecasts.json** - All forecasts in JSON format
- **outputs/summary.json** - Training summary and statistics
- **outputs/training.log** - Detailed training logs
- **saved_models/** - Trained model files

---

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check API health |
| `/states` | GET | List all states |
| `/forecast/{state}` | GET | Get 8-week forecast |
| `/forecast-all` | GET | Get all forecasts |
| `/models` | GET | View trained models |
| `/retrain` | POST | Retrain all models |
| `/docs` | GET | Interactive API docs |

---

## Example API Calls

### Get forecast for California
```bash
curl http://localhost:8000/forecast/California
```

### Get all states
```bash
curl http://localhost:8000/states
```

### Get model information
```bash
curl http://localhost:8000/models
```

### Retrain models
```bash
curl -X POST http://localhost:8000/retrain
```

---

## Troubleshooting

**Problem: "No Excel file found"**
- Solution: Ensure `Forecasting Case- Study.xlsx` is in the project root

**Problem: Import errors**
- Solution: Run `pip install -r requirements.txt`

**Problem: API port already in use**
- Solution: Use different port: `uvicorn app.main:app --port 8001`

**Problem: Out of memory**
- Solution: Run `test_quick.py` first with 2 states instead of full training

---

## Project Structure

```
forecasting-system/
├── app/                    # Main application code
│   ├── models/            # Forecasting models
│   ├── services/          # Business logic
│   ├── api/               # REST API endpoints
│   └── main.py            # FastAPI application
├── outputs/               # Generated forecasts and reports
├── saved_models/          # Trained models
├── run_training.py        # Training script
├── example_api_client.py  # API client examples
└── requirements.txt       # Dependencies
```

---

## System Architecture

```
Excel Data
    ↓
[Data Preprocessing]
    ↓
[Feature Engineering]
    ↓
├─→ [SARIMA Model]
├─→ [Prophet Model]  
├─→ [XGBoost Model]
└─→ [LSTM Model]
    ↓
[Model Evaluation & Selection]
    ↓
[Forecast Generation]
    ↓
[REST API Service]
    ↓
JSON/CSV Output
```

---

## Model Selection

The system automatically selects the best model per state based on RMSE (Root Mean Squared Error) on validation data.

Models trained:
- **SARIMA**: Statistical time series model
- **Prophet**: Facebook's forecasting library
- **XGBoost**: Gradient boosting with features
- **LSTM**: Neural network model

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Run training
3. ✅ Start API server
4. ✅ Test endpoints
5. View detailed documentation in README.md
6. View API documentation in API_DOCUMENTATION.md
7. Integrate with your application

---

## Support

For detailed information:
- See [README.md](README.md) for full documentation
- See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
- Check [outputs/training.log](outputs/training.log) for execution logs
