"""
Example API Usage Patterns
Demonstrates how to use the Time Series Forecasting API
"""

import requests
import pandas as pd
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000"

# ============================================================================
# EXAMPLE 1: Get List of All States
# ============================================================================

def example_get_all_states():
    """Get list of all 43 forecasted states"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Get All States")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/states")
    data = response.json()
    
    print(f"Total States: {data['total_states']}")
    print(f"States: {', '.join(data['states'][:10])}...")


# ============================================================================
# EXAMPLE 2: Get Forecast for a Single State
# ============================================================================

def example_get_single_state_forecast():
    """Get 56-day forecast for a specific state"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Get Single State Forecast")
    print("="*80)
    
    state = "California"
    response = requests.get(f"{BASE_URL}/forecast/{state}")
    data = response.json()
    
    print(f"State: {data['state']}")
    print(f"Best Model: {data['best_model']}")
    print(f"Forecast Horizon: {data['forecast_horizon_days']} days")
    print("\nFirst 7 days of forecast:")
    
    for i, forecast in enumerate(data['forecast'][:7], 1):
        print(f"  Day {i}: {forecast['date']} → ${forecast['predicted_sales']:,.0f}")
    
    return data


# ============================================================================
# EXAMPLE 3: Get All Model Metrics
# ============================================================================

def example_get_model_metrics():
    """Get model performance metrics across all states"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Get Model Metrics")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/models")
    data = response.json()
    
    print(f"Total States: {data['total_states']}")
    print(f"Model Distribution:")
    for model, count in data['model_count'].items():
        print(f"  {model}: {count} states ({count/data['total_states']*100:.1f}%)")


# ============================================================================
# EXAMPLE 4: Analyze Forecast Data
# ============================================================================

def example_analyze_forecast():
    """Analyze forecast data for multiple states"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Analyze Forecast Data")
    print("="*80)
    
    states = ["California", "Texas", "New York"]
    all_forecasts = []
    
    for state in states:
        response = requests.get(f"{BASE_URL}/forecast/{state}")
        data = response.json()
        
        # Convert to DataFrame for easy analysis
        df = pd.DataFrame(data['forecast'])
        df['state'] = state
        all_forecasts.append(df)
        
        # Calculate statistics
        min_sales = df['predicted_sales'].min()
        max_sales = df['predicted_sales'].max()
        avg_sales = df['predicted_sales'].mean()
        
        print(f"\n{state}:")
        print(f"  Min: ${min_sales:,.0f}")
        print(f"  Max: ${max_sales:,.0f}")
        print(f"  Average: ${avg_sales:,.0f}")
        print(f"  Range: ${max_sales - min_sales:,.0f}")
    
    # Combine all forecasts
    combined_df = pd.concat(all_forecasts, ignore_index=True)
    return combined_df


# ============================================================================
# EXAMPLE 5: Export Forecast to CSV
# ============================================================================

def example_export_forecast_to_csv():
    """Export forecasts for all states to CSV"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Export Forecasts to CSV")
    print("="*80)
    
    # Get all states
    states_response = requests.get(f"{BASE_URL}/states")
    states = states_response.json()['states']
    
    all_forecasts = []
    
    for state in states[:3]:  # Demo with first 3 states
        response = requests.get(f"{BASE_URL}/forecast/{state}")
        data = response.json()
        
        for forecast in data['forecast']:
            all_forecasts.append({
                'date': forecast['date'],
                'state': state,
                'predicted_sales': forecast['predicted_sales'],
                'best_model': data['best_model']
            })
    
    # Create DataFrame and save
    df = pd.DataFrame(all_forecasts)
    output_file = "forecast_export.csv"
    df.to_csv(output_file, index=False)
    print(f"✓ Exported {len(df)} forecasts to {output_file}")
    
    return df


# ============================================================================
# EXAMPLE 6: Compare Forecasts Across States
# ============================================================================

def example_compare_forecasts():
    """Compare 56-day total sales across states"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Compare Forecasts Across States")
    print("="*80)
    
    # Get states
    states_response = requests.get(f"{BASE_URL}/states")
    states = states_response.json()['states']
    
    state_totals = []
    
    for state in states:
        response = requests.get(f"{BASE_URL}/forecast/{state}")
        data = response.json()
        
        total_sales = sum(f['predicted_sales'] for f in data['forecast'])
        avg_daily_sales = total_sales / len(data['forecast'])
        
        state_totals.append({
            'state': state,
            'total_56_day_sales': total_sales,
            'avg_daily_sales': avg_daily_sales,
            'best_model': data['best_model']
        })
    
    # Sort by total sales
    sorted_states = sorted(state_totals, key=lambda x: x['total_56_day_sales'], reverse=True)
    
    print("\nTop 10 States by 56-Day Forecast Sales:")
    for i, item in enumerate(sorted_states[:10], 1):
        print(f"{i:2d}. {item['state']:20s} → ${item['total_56_day_sales']:>15,.0f} " +
              f"(${item['avg_daily_sales']:>12,.0f}/day)")
    
    return sorted_states


# ============================================================================
# EXAMPLE 7: API Health Check
# ============================================================================

def example_health_check():
    """Check API health and connectivity"""
    print("\n" + "="*80)
    print("EXAMPLE 7: API Health Check")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()
        
        print(f"✓ API Status: {data['status']}")
        print(f"✓ Message: {data['message']}")
        print(f"✓ API is running at {BASE_URL}")
        print(f"✓ API Documentation: {BASE_URL}/docs")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ API Error: {e}")
        print(f"✗ Make sure API is running: uvicorn app.main:app --reload")
        return False


# ============================================================================
# EXAMPLE 8: Batch Forecast Retrieval
# ============================================================================

def example_batch_forecast_retrieval():
    """Efficiently retrieve forecasts for multiple states"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Batch Forecast Retrieval")
    print("="*80)
    
    states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California"]
    
    print(f"Retrieving forecasts for {len(states)} states...")
    
    batch_results = {}
    for state in states:
        try:
            response = requests.get(f"{BASE_URL}/forecast/{state}")
            if response.status_code == 200:
                batch_results[state] = response.json()
                print(f"  ✓ {state}")
            else:
                print(f"  ✗ {state} (HTTP {response.status_code})")
        except Exception as e:
            print(f"  ✗ {state} (Error: {e})")
    
    print(f"\nSuccessfully retrieved {len(batch_results)}/{len(states)} forecasts")
    return batch_results


# ============================================================================
# EXAMPLE 9: Create Forecast Summary Report
# ============================================================================

def example_summary_report():
    """Create a summary report of all forecasts"""
    print("\n" + "="*80)
    print("EXAMPLE 9: Summary Report")
    print("="*80)
    
    # Get states
    states_response = requests.get(f"{BASE_URL}/states")
    total_states = states_response.json()['total_states']
    
    # Get models
    models_response = requests.get(f"{BASE_URL}/models")
    models_data = models_response.json()
    
    # Get first forecast for sample dates
    sample_state = "California"
    response = requests.get(f"{BASE_URL}/forecast/{sample_state}")
    sample_forecast = response.json()['forecast']
    
    print(f"\nForecasting System Summary Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    print(f"\nGeographic Coverage:")
    print(f"  Total States: {total_states}")
    print(f"  Region: United States")
    
    print(f"\nModel Performance:")
    for model, count in models_data['model_count'].items():
        if count > 0:
            print(f"  {model}: {count} states")
    
    print(f"\nForecast Details:")
    print(f"  Horizon: 56 days")
    print(f"  Start Date: {sample_forecast[0]['date']}")
    print(f"  End Date: {sample_forecast[-1]['date']}")
    print(f"  Total Predictions: {total_states * 56}")
    
    print(f"\nSample Forecast (California - First 3 Days):")
    for forecast in sample_forecast[:3]:
        print(f"  {forecast['date']}: ${forecast['predicted_sales']:>15,.0f}")


# ============================================================================
# EXAMPLE 10: Error Handling
# ============================================================================

def example_error_handling():
    """Demonstrate proper error handling"""
    print("\n" + "="*80)
    print("EXAMPLE 10: Error Handling")
    print("="*80)
    
    # Test 1: Invalid state
    print("\nTest 1: Requesting invalid state")
    try:
        response = requests.get(f"{BASE_URL}/forecast/InvalidState")
        if response.status_code == 404:
            print(f"✓ Correctly handled 404: {response.json()['detail']}")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: API not running
    print("\nTest 2: Checking API connectivity")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"✓ API is running")
    except requests.exceptions.ConnectionError:
        print(f"✗ Could not connect to API. Start server: uvicorn app.main:app --reload")
    except requests.exceptions.Timeout:
        print(f"✗ API request timed out")
    
    # Test 3: Large batch handling
    print("\nTest 3: Batch request handling")
    try:
        states_response = requests.get(f"{BASE_URL}/states")
        states = states_response.json()['states']
        print(f"✓ Successfully retrieved {len(states)} states")
    except Exception as e:
        print(f"✗ Error: {e}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TIME SERIES FORECASTING API - EXAMPLE USAGE")
    print("="*80)
    
    # Run all examples
    if example_health_check():
        example_get_all_states()
        example_get_single_state_forecast()
        example_get_model_metrics()
        example_analyze_forecast()
        example_export_forecast_to_csv()
        example_compare_forecasts()
        example_batch_forecast_retrieval()
        example_summary_report()
        example_error_handling()
        
        print("\n" + "="*80)
        print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nNext Steps:")
        print("1. Check API documentation: http://localhost:8000/docs")
        print("2. Read SYSTEM_READY.md for complete documentation")
        print("3. Integrate API with your application")
        print("4. Deploy to production when ready")
        print("\n")
    else:
        print("\n✗ Cannot proceed - API is not running")
        print("Start the API with: uvicorn app.main:app --reload")
