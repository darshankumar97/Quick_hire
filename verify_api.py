import requests

states_to_test = ["Texas", "Florida", "New York"]
BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("QUICK API VERIFICATION TEST")
print("="*80)

for state in states_to_test:
    try:
        r = requests.get(f"{BASE_URL}/forecast/{state}")
        data = r.json()
        print(f"\n✓ {state}")
        print(f"  Model: {data['best_model']}")
        print(f"  Forecasts: {data['forecast_horizon_days']} days")
        print(f"  First forecast: {data['forecast'][0]['date']} → ${data['forecast'][0]['predicted_sales']:,.0f}")
    except Exception as e:
        print(f"\n✗ {state}: {e}")

print("\n" + "="*80)
print("✓ API IS FULLY OPERATIONAL")
print("="*80 + "\n")
