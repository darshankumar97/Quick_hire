"""
Example API client - demonstrates how to use the forecasting API
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"


def get_health():
    """Check API health status"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Status:")
    print(json.dumps(response.json(), indent=2))
    return response.ok


def get_states():
    """Get list of available states"""
    response = requests.get(f"{BASE_URL}/states")
    data = response.json()
    print(f"\nAvailable States ({data['total_states']} total):")
    states = data['states']
    # Print in columns
    for i in range(0, len(states), 5):
        print("  " + ", ".join(states[i:i+5]))
    return states


def get_models():
    """Get trained models information"""
    response = requests.get(f"{BASE_URL}/models")
    data = response.json()
    print("\nTrained Models:")
    print(f"  Total States: {data['total_states']}")
    print("\nModel Distribution:")
    for model, count in data['model_count'].items():
        print(f"  {model}: {count} states")
    return data


def get_forecast(state):
    """Get forecast for a specific state"""
    response = requests.get(f"{BASE_URL}/forecast/{state}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nForecast for {state} (using {data['best_model']} model):")
        print(f"Forecast horizon: {data['forecast_horizon_days']} days\n")
        print(f"{'Date':<12} {'Predicted Sales':>20}")
        print("-" * 35)
        for item in data['forecast'][:10]:  # Show first 10
            date_str = item['date']
            sales = item['predicted_sales']
            print(f"{date_str:<12} ${sales:>18,.0f}")
        print("...")
        return data['forecast']
    else:
        print(f"Error: {response.json()}")
        return None


def get_all_forecasts():
    """Get forecasts for all states"""
    response = requests.get(f"{BASE_URL}/forecast-all")
    if response.status_code == 200:
        data = response.json()
        print(f"\nTotal States: {data['total_states']}")
        print(f"Forecast horizon: {data['forecast_horizon_days']} days")
        
        # Show sample for first state
        first_state = list(data['forecasts'].keys())[0]
        print(f"\nSample (first 5 forecasts for {first_state}):")
        for forecast in data['forecasts'][first_state][:5]:
            print(f"  {forecast['date']}: ${forecast['predicted_sales']:,.0f}")
        
        return data
    else:
        print(f"Error: {response.json()}")
        return None


def retrain_models():
    """Trigger model retraining"""
    print("\nRetraining models (this may take a few minutes)...")
    response = requests.post(f"{BASE_URL}/retrain")
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Successfully retrained: {data['successful_states']}/{data['total_states']} states")
        print(f"Output files: {', '.join(list(data['output_files'].values()))}")
        return data
    else:
        print(f"Error: {response.json()}")
        return None


def main():
    """Run example API calls"""
    print("=" * 60)
    print("Time Series Forecasting API - Example Client")
    print("=" * 60)
    
    try:
        # Check health
        if not get_health():
            print("\nAPI is not responding. Make sure the server is running:")
            print("  uvicorn app.main:app --reload")
            return
        
        # Get states
        states = get_states()
        
        # Get models
        get_models()
        
        # Get forecast for a specific state
        if states:
            state = states[0]  # First state
            forecast = get_forecast(state)
        
        # Get all forecasts (large response)
        # Uncomment to run:
        # get_all_forecasts()
        
        print("\n" + "=" * 60)
        print("Examples of other API calls:")
        print("=" * 60)
        print("""
1. Get health status:
   curl http://localhost:8000/health

2. Get states:
   curl http://localhost:8000/states

3. Get models info:
   curl http://localhost:8000/models

4. Get forecast for California:
   curl http://localhost:8000/forecast/California

5. Retrain models (POST):
   curl -X POST http://localhost:8000/retrain

6. API Documentation:
   Open http://localhost:8000/docs in your browser
        """)
        
    except requests.exceptions.ConnectionError:
        print("\n" + "=" * 60)
        print("ERROR: Cannot connect to API")
        print("=" * 60)
        print("\nMake sure the API server is running:")
        print("\n  cd forecasting-system")
        print("  uvicorn app.main:app --reload")
        print("\nThen run this script again.")


if __name__ == "__main__":
    main()
