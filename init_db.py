#!/usr/bin/env python3
"""
Database initialization script for AI Task Planning Agent
Creates database tables and optionally loads sample data
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import DatabaseManager
from database.models import Base
from agent.mock_agent import MockTaskPlanningAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def init_database(load_sample_data: bool = False) -> bool:
    """
    Initialize the database with tables and optionally sample data
    
    Args:
        load_sample_data (bool): Whether to load sample plans
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Initializing database...")
        
        # Create database manager
        db_manager = DatabaseManager()
        
        logger.info("Database tables created successfully")
        
        if load_sample_data:
            logger.info("Loading sample data...")
            load_sample_plans(db_manager)
        
        # Verify database
        stats = db_manager.get_plan_statistics()
        logger.info(f"Database initialized with {stats['total_plans']} plans")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

def load_sample_plans(db_manager: DatabaseManager) -> None:
    """
    Load sample plans into the database for testing
    
    Args:
        db_manager: Database manager instance
    """
    sample_goals = [
        "Plan a 3-day trip to Jaipur with cultural highlights and good food",
        "Organise a 5-step daily study routine for learning Python",
        "Create a weekend plan in Vizag with beach, hiking, and seafood",
        "Plan a 2-day vegetarian food tour in Hyderabad",
        "Design a home workout routine for beginners"
    ]
    
    # Use mock agent to generate sample plans
    agent = MockTaskPlanningAgent()
    
    for goal in sample_goals:
        try:
            logger.info(f"Creating sample plan: {goal[:50]}...")
            plan_data = agent.create_plan(goal)
            
            if plan_data:
                plan_id = db_manager.save_plan(plan_data)
                if plan_id:
                    logger.info(f"Sample plan created with ID: {plan_id}")
                else:
                    logger.warning(f"Failed to save sample plan: {goal}")
            else:
                logger.warning(f"Failed to generate sample plan: {goal}")
                
        except Exception as e:
            logger.error(f"Error creating sample plan '{goal}': {e}")

def check_database_health() -> bool:
    """
    Check database health and connectivity
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        db_manager = DatabaseManager()
        stats = db_manager.get_plan_statistics()
        
        logger.info("Database Health Check:")
        logger.info(f"  Total Plans: {stats.get('total_plans', 'Unknown')}")
        logger.info(f"  Total Steps: {stats.get('total_steps', 'Unknown')}")
        logger.info(f"  Recent Plans (7 days): {stats.get('recent_plans', 'Unknown')}")
        logger.info(f"  Database URL: {stats.get('database_url', 'Unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

def reset_database() -> bool:
    """
    Reset the database by dropping and recreating all tables
    WARNING: This will delete all existing data!
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.warning("RESETTING DATABASE - ALL DATA WILL BE LOST!")
        
        # Create database manager
        db_manager = DatabaseManager()
        
        # Drop all tables
        Base.metadata.drop_all(bind=db_manager.engine)
        logger.info("All tables dropped")
        
        # Recreate tables
        Base.metadata.create_all(bind=db_manager.engine)
        logger.info("Tables recreated")
        
        return True
        
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return False

def main():
    """
    Main function to handle command line arguments
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization script")
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="Reset database (WARNING: Deletes all data)"
    )
    parser.add_argument(
        "--sample-data", 
        action="store_true", 
        help="Load sample data after initialization"
    )
    parser.add_argument(
        "--health-check", 
        action="store_true", 
        help="Check database health"
    )
    
    args = parser.parse_args()
    
    if args.health_check:
        logger.info("Running database health check...")
        if check_database_health():
            logger.info("Database is healthy")
            sys.exit(0)
        else:
            logger.error("Database health check failed")
            sys.exit(1)
    
    if args.reset:
        confirmation = input("Are you sure you want to reset the database? All data will be lost! (yes/no): ")
        if confirmation.lower() != 'yes':
            logger.info("Database reset cancelled")
            sys.exit(0)
        
        if not reset_database():
            logger.error("Database reset failed")
            sys.exit(1)
    
    # Initialize database
    if init_database(load_sample_data=args.sample_data):
        logger.info("Database initialization completed successfully")
        sys.exit(0)
    else:
        logger.error("Database initialization failed")
        sys.exit(1)

if __name__ == "__main__":
    main()