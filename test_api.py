"""
Test API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("TESTING FORECASTING API")
print("="*80)

# Test 1: Health Check
print("\n[1] Testing /health endpoint...")
try:
    r = requests.get(f"{BASE_URL}/health")
    print(f"✓ Status: {r.json()['status']}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Get States
print("\n[2] Testing /states endpoint...")
try:
    r = requests.get(f"{BASE_URL}/states")
    data = r.json()
    print(f"✓ Total States: {data['total_states']}")
    print(f"✓ Sample States: {', '.join(data['states'][:5])}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Get Models Information
print("\n[3] Testing /models endpoint...")
try:
    r = requests.get(f"{BASE_URL}/models")
    data = r.json()
    print(f"✓ Total States with Models: {data['total_states']}")
    if 'model_count' in data:
        print(f"✓ Model Distribution:")
        for model, count in data['model_count'].items():
            print(f"  - {model}: {count} states")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Get Forecast for a Specific State
print("\n[4] Testing /forecast/Alabama endpoint...")
try:
    r = requests.get(f"{BASE_URL}/forecast/Alabama")
    data = r.json()
    print(f"✓ State: {data['state']}")
    print(f"✓ Best Model: {data['best_model']}")
    print(f"✓ Forecast Horizon: {data['forecast_horizon_days']} days")
    print(f"✓ Sample Forecasts:")
    for i, forecast in enumerate(data['forecast'][:3]):
        print(f"  - {forecast['date']}: ${forecast['predicted_sales']:,.0f}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Get Root Information
print("\n[5] Testing root / endpoint...")
try:
    r = requests.get(f"{BASE_URL}/")
    data = r.json()
    print(f"✓ API Version: {data['version']}")
    print(f"✓ Available Endpoints:")
    for endpoint, path in data['endpoints'].items():
        print(f"  - {endpoint}: {path}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*80)
print("API TEST COMPLETE")
print("="*80)
print(f"\nAPI Documentation: http://localhost:8000/docs")
print(f"Alternative Docs: http://localhost:8000/redoc")
print("\n")
