"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from pathlib import Path

from app.api.routes import router, initialize_services

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Time Series Forecasting API",
    description="Production-ready forecasting system for sales prediction",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on app startup"""
    try:
        logger.info("Initializing forecasting system...")
        
        # Find Excel file in project root
        base_dir = Path(__file__).parent.parent
        excel_file = None
        
        # Look for Excel file in root directory
        for file in base_dir.glob("*.xlsx"):
            excel_file = str(file)
            logger.info(f"Found Excel file: {excel_file}")
            break
        
        # If not found, try with exact name
        if not excel_file:
            exact_file = base_dir / "Forecasting Case- Study.xlsx"
            if exact_file.exists():
                excel_file = str(exact_file)
                logger.info(f"Found Excel file: {excel_file}")
        
        if excel_file:
            initialize_services(excel_file)
            logger.info("Services initialized successfully")
        else:
            logger.warning("No Excel file found in project root - forecasts will be loaded from CSV")
            # Initialize with None - forecasts will be loaded from CSV
            initialize_services(None)
            logger.info("Services initialized with CSV forecast loading")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Time Series Forecasting API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "models": "/models",
            "states": "/states",
            "forecast": "/forecast/{state}",
            "all_forecasts": "/forecast-all",
            "retrain": "/retrain (POST)"
        },
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
