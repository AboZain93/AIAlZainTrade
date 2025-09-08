"""
Main entry point for AIAlZainTrade
Alternative to running with uvicorn directly
"""

import uvicorn
from backend.main import app
from config.settings import get_settings, create_env_file

settings = get_settings()

def main():
    """Main function to run the application"""
    # Create .env file if it doesn't exist
    create_env_file()
    
    # Run the application
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()