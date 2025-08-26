#!/usr/bin/env python3
"""
Database initialization script for APPETIT backend.

This script handles:
- Database creation (for PostgreSQL)
- Running Alembic migrations
- Optional initial data seeding

Usage:
    python scripts/init_db.py [--seed-data] [--force-recreate]
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.db.session import engine, SessionLocal
from sqlalchemy import create_engine, text
import logging

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_database_if_not_exists():
    """Create database if it doesn't exist (PostgreSQL only)."""
    database_url = settings.DATABASE_URL
    
    if not database_url.startswith("postgresql"):
        logger.info("Database URL is not PostgreSQL, skipping database creation")
        return True
    
    try:
        # parse database URL to get database name
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        database_name = parsed.path[1:]  # Remove leading '/'
        
        # create connection to postgres database (without specific DB)
        # properly reconstruct URL to avoid replacing database name in other parts (like username)
        postgres_url = f"{parsed.scheme}://{parsed.netloc}/postgres"
        postgres_engine = create_engine(postgres_url)
        
        # check if database exists
        with postgres_engine.connect() as conn:
            conn.execute(text("COMMIT"))  # End any existing transaction
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": database_name}
            )
            
            if result.fetchone() is None:
                logger.info(f"Creating database: {database_name}")
                # create database
                conn.execute(text(f'CREATE DATABASE "{database_name}"'))
                logger.info(f"Database {database_name} created successfully")
            else:
                logger.info(f"Database {database_name} already exists")
                
        postgres_engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False


def run_migrations():
    """Run Alembic migrations to create/update schema."""
    try:
        logger.info("Running Alembic migrations...")
        
        # change to project root directory
        os.chdir(project_root)
        
        # run alembic upgrade head
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("Migrations completed successfully")
        logger.debug(f"Migration output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running migrations: {e}")
        logger.error(f"Migration error output: {e.stderr}")
        return False


def seed_initial_data():
    """Seed initial data (categories, admin user, etc.)."""
    try:
        logger.info("Seeding initial data...")
        
        # import models and dependencies with proper error handling
        try:
            from app.models.models import User, Category
            from app.core.security import get_password_hash
            from datetime import datetime
        except ImportError as e:
            logger.error(f"Import error during seeding: {e}")
            return False
        
        db = SessionLocal()
        try:
            # create default categories
            default_categories = [
                {"name": "Appetizers", "sort": 1},
                {"name": "Main Courses", "sort": 2},
                {"name": "Desserts", "sort": 3},
                {"name": "Beverages", "sort": 4},
            ]
            
            for cat_data in default_categories:
                existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
                if not existing:
                    category = Category(**cat_data)
                    db.add(category)
                    logger.info(f"Created category: {cat_data['name']}")
            
            # create default admin user
            admin_email = "admin@ium.app"
            existing_admin = db.query(User).filter(User.email == admin_email).first()
            
            if not existing_admin:
                admin_user = User(
                    full_name="APPETIT Admin",
                    email=admin_email,
                    password_hash=get_password_hash("admin123"),
                    role="admin",
                    is_email_verified=True,
                    created_at=datetime.utcnow()
                )
                db.add(admin_user)
                logger.info(f"Created admin user: {admin_email}")
            
            db.commit()
            logger.info("Initial data seeded successfully")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error seeding initial data: {e}")
        return False


def check_database_connection():
    """Check if database connection is working."""
    try:
        logger.info("Testing database connection...")
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            
        logger.info("Database connection successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Initialize APPETIT database")
    parser.add_argument(
        "--seed-data",
        action="store_true",
        help="Seed initial data (categories, admin user)"
    )
    parser.add_argument(
        "--force-recreate",
        action="store_true",
        help="Force recreate database (PostgreSQL only, DESTRUCTIVE)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check database connection, don't run migrations"
    )
    
    args = parser.parse_args()
    
    logger.info("Starting database initialization...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    # check if we should force recreate database
    if args.force_recreate:
        logger.warning("Force recreate requested - this will DELETE existing database!")
        confirm = input("Are you sure? Type 'yes' to continue: ")
        if confirm.lower() != 'yes':
            logger.info("Operation cancelled")
            return False
    
    # step 1: Create database if needed (skip for non-PostgreSQL when only checking)
    if args.check_only and not settings.DATABASE_URL.startswith("postgresql"):
        logger.info("Skipping database creation for non-PostgreSQL database in check-only mode")
    else:
        if not create_database_if_not_exists():
            logger.error("Failed to create database")
            return False
    
    # step 2: Check database connection
    if not check_database_connection():
        logger.error("Database connection failed")
        return False
    
    if args.check_only:
        logger.info("Database check completed successfully")
        return True
    
    # step 3: Run migrations
    if not run_migrations():
        logger.error("Migration failed")
        return False
    
    # step 4: Seed initial data if requested
    if args.seed_data:
        if not seed_initial_data():
            logger.error("Data seeding failed")
            return False
    
    logger.info("Database initialization completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)