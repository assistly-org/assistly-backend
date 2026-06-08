from sqlalchemy import text
from app.infrastructure.db.database import engine
from app.infrastructure.logger import logger

def test_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("SUCCESS: Successfully connected to your Supabase PostgreSQL instance!")
            
    except Exception as e:
        logger.error(f"FAILED: Could not connect to Supabase. Details: {e}")

if __name__ == "__main__":
    test_connection()