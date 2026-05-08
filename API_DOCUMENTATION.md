# API Documentation

Time Series Forecasting System REST API

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. This can be added in a production environment using API keys, JWT tokens, or OAuth2.

## Response Format

All responses are in JSON format with the following structure:

```json
{
  "status": "success|error",
  "data": { ... },
  "message": "description"
}
```

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "message": "Time Series Forecasting API is running"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Get Available States

**Endpoint:** `GET /states`

**Description:** Get list of all states available in the dataset.

**Response:**
```json
{
  "total_states": 51,
  "states": [
    "Alabama",
    "Alaska",
    ...
    "Wyoming"
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/states
```

---

### 3. Get Forecast for a State

**Endpoint:** `GET /forecast/{state}`

**Description:** Get 8-week (56-day) forecast for a specific state.

**Parameters:**
- `state` (string, required): State name (e.g., "California", "Texas")

**Response:**
```json
{
  "state": "California",
  "best_model": "Prophet",
  "forecast_horizon_days": 56,
  "forecast": [
    {
      "date": "2026-06-01",
      "predicted_sales": 450000000.50
    },
    {
      "date": "2026-06-02",
      "predicted_sales": 451000000.20
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/forecast/California
```

**Error Response (404):**
```json
{
  "detail": "No forecast found for {state}"
}
```

---

### 4. Get All Forecasts

**Endpoint:** `GET /forecast-all`

**Description:** Get forecasts for all states (large response).

**Response:**
```json
{
  "total_states": 51,
  "forecast_horizon_days": 56,
  "forecasts": {
    "Alabama": [
      {
        "date": "2026-06-01",
        "predicted_sales": 209893733.45
      }
    ],
    "Alaska": [ ... ],
    ...
  }
}
```

**Example:**
```bash
curl http://localhost:8000/forecast-all
```

---

### 5. Get Models Information

**Endpoint:** `GET /models`

**Description:** Get information about trained models and their performance.

**Response:**
```json
{
  "message": "Model information",
  "total_states": 51,
  "best_models": {
    "Alabama": "SARIMA",
    "Alaska": "Prophet",
    "Arizona": "XGBoost",
    ...
  },
  "model_count": {
    "SARIMA": 25,
    "Prophet": 15,
    "XGBoost": 8,
    "LSTM": 3
  }
}
```

**Example:**
```bash
curl http://localhost:8000/models
```

---

### 6. Retrain Models

**Endpoint:** `POST /retrain`

**Description:** Retrain all models with latest data. This is a synchronous operation and may take several minutes.

**Request:**
```bash
curl -X POST http://localhost:8000/retrain
```

**Response:**
```json
{
  "status": "success",
  "message": "Models retrained successfully",
  "total_states": 51,
  "successful_states": 50,
  "output_files": {
    "csv": "C:\\Projects\\forecasting-system\\outputs\\forecasts.csv",
    "json": "C:\\Projects\\forecasting-system\\outputs\\forecasts.json"
  }
}
```

---

## Usage Examples

### Python Example

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Get forecast for California
response = requests.get(f"{BASE_URL}/forecast/California")
forecast_data = response.json()

print(f"State: {forecast_data['state']}")
print(f"Best Model: {forecast_data['best_model']}")

# Display first 5 forecasts
for forecast in forecast_data['forecast'][:5]:
    print(f"{forecast['date']}: ${forecast['predicted_sales']:,.0f}")
```

### JavaScript Example

```javascript
const BASE_URL = "http://localhost:8000";

// Get forecast for New York
fetch(`${BASE_URL}/forecast/New York`)
  .then(response => response.json())
  .then(data => {
    console.log(`State: ${data.state}`);
    console.log(`Best Model: ${data.best_model}`);
    
    // Display forecasts
    data.forecast.slice(0, 5).forEach(forecast => {
      console.log(`${forecast.date}: $${forecast.predicted_sales.toLocaleString()}`);
    });
  });
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Get states
curl http://localhost:8000/states

# Get forecast for Texas
curl http://localhost:8000/forecast/Texas

# Get models info
curl http://localhost:8000/models

# Retrain models (may take time)
curl -X POST http://localhost:8000/retrain
```

---

## Error Handling

The API returns appropriate HTTP status codes:

- **200 OK**: Request successful
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side error

### Error Response Format

```json
{
  "detail": "Error description"
}
```

### Example Error

```bash
$ curl http://localhost:8000/forecast/InvalidState

{
  "detail": "No forecast found for InvalidState"
}
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. In production, consider adding:
- Request throttling
- API key quotas
- Per-IP request limits

---

## Performance Considerations

### Response Times

- `/health`: < 10ms
- `/states`: < 50ms
- `/forecast/{state}`: < 100ms
- `/models`: < 100ms
- `/forecast-all`: 1-2 seconds (large response)
- `/retrain`: 10-30 minutes (depends on data size)

### Data Size

- Typical forecast response: 10-20 KB per state
- All forecasts response: 1-2 MB for 50 states

### Optimization Tips

1. Cache forecast responses if they don't change frequently
2. Use `/forecast/{state}` instead of `/forecast-all` when possible
3. Schedule `/retrain` during off-peak hours

---

## Integration Examples

### Scheduling Retraining

```python
import schedule
import requests
import time

def retrain():
    requests.post("http://localhost:8000/retrain")
    print("Models retrained successfully")

# Retrain weekly on Sundays at 2 AM
schedule.every().sunday.at("02:00").do(retrain)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Dashboard Integration

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

@app.get("/dashboard")
async def dashboard():
    # Fetch latest forecasts
    forecasts = requests.get("http://localhost:8000/forecast-all").json()
    
    # Build HTML dashboard
    html = "<h1>Sales Forecasts</h1>"
    html += f"<p>Updated: {datetime.now()}</p>"
    # ... more HTML ...
    
    return HTMLResponse(content=html)
```

---

## Future Enhancements

1. **Authentication**: Add API key or JWT authentication
2. **Rate Limiting**: Implement per-client rate limits
3. **Caching**: Cache frequently requested forecasts
4. **Webhooks**: Send predictions to external systems
5. **Batch Endpoints**: Request multiple states in single call
6. **Historical Data**: Retrieve past forecast accuracy
7. **Sensitivity Analysis**: What-if scenario analysis
8. **Export Formats**: XML, CSV, Parquet export options

---

## Support

For API issues or questions:
1. Check server logs: `outputs/training.log`
2. Review endpoint documentation: `http://localhost:8000/docs`
3. Test with example client: `python example_api_client.py`
