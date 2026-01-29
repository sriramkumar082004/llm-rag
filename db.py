import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Database configuration from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", 5432)),
}

# Connection pool for efficient database access
connection_pool = None


def initialize_pool(minconn=1, maxconn=10):
    """Initialize the connection pool."""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn, maxconn, **DB_CONFIG
        )
        logger.info("✅ Database connection pool initialized successfully")
        return connection_pool
    except Exception as e:
        logger.error(f"❌ Failed to initialize connection pool: {e}")
        raise


def get_db_connection():
    """Get a connection from the pool."""
    global connection_pool

    if connection_pool is None:
        initialize_pool()

    try:
        conn = connection_pool.getconn()
        logger.info("✅ Database connection acquired from pool")
        return conn
    except Exception as e:
        logger.error(f"❌ Failed to get connection from pool: {e}")
        raise


def release_db_connection(conn):
    """Return a connection to the pool."""
    global connection_pool

    if connection_pool is not None and conn is not None:
        connection_pool.putconn(conn)
        logger.info("✅ Database connection returned to pool")


def close_all_connections():
    """Close all connections in the pool."""
    global connection_pool

    if connection_pool is not None:
        connection_pool.closeall()
        logger.info("✅ All database connections closed")


class DatabaseConnection:
    """Context manager for database connections."""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Rollback on error
            self.conn.rollback()
            logger.error(f"❌ Transaction rolled back due to error: {exc_val}")
        else:
            # Commit on success
            self.conn.commit()

        if self.cursor:
            self.cursor.close()

        release_db_connection(self.conn)

        # Return False to propagate exceptions
        return False


def test_connection():
    """Test the database connection."""
    try:
        with DatabaseConnection() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            logger.info(f"✅ Database connection successful!")
            logger.info(f"PostgreSQL version: {version[0]}")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection when run directly
    logging.basicConfig(level=logging.INFO)
    print("Testing database connection...")
    if test_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
    close_all_connections()
