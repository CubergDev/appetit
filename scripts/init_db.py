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


def delete_all_data():
    """Delete all existing data from database tables in proper order."""
    try:
        logger.info("Deleting all existing data...")
        
        # import models with proper error handling
        try:
            from app.models.models import (
                User, Category, MenuItem, SavedAddress, Order, OrderItem, 
                Promocode, PromoBatch, Device, EmailVerification, 
                PhoneVerification, EmailEvent
            )
        except ImportError as e:
            logger.error(f"Import error during data deletion: {e}")
            return False
        
        db = SessionLocal()
        try:
            # delete in order respecting foreign key constraints
            # child tables first, then parent tables
            
            logger.info("Deleting order items...")
            db.query(OrderItem).delete()
            
            logger.info("Deleting orders...")
            db.query(Order).delete()
            
            logger.info("Deleting saved addresses...")
            db.query(SavedAddress).delete()
            
            logger.info("Deleting devices...")
            db.query(Device).delete()
            
            logger.info("Deleting email verifications...")
            db.query(EmailVerification).delete()
            
            logger.info("Deleting phone verifications...")
            db.query(PhoneVerification).delete()
            
            logger.info("Deleting email events...")
            db.query(EmailEvent).delete()
            
            logger.info("Deleting menu items...")
            db.query(MenuItem).delete()
            
            logger.info("Deleting users...")
            db.query(User).delete()
            
            logger.info("Deleting categories...")
            db.query(Category).delete()
            
            logger.info("Deleting promocodes...")
            db.query(Promocode).delete()
            
            logger.info("Deleting promo batches...")
            db.query(PromoBatch).delete()
            
            db.commit()
            logger.info("All existing data deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during data deletion: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error deleting data: {e}")
        return False


def seed_initial_data():
    """Delete all data, run migrations, and seed initial data (categories, admin user, plain users with realistic data, etc.)."""
    try:
        logger.info("Starting data seeding process...")
        
        # step 1: delete all existing data
        if not delete_all_data():
            logger.error("Failed to delete existing data")
            return False
        
        logger.info("Seeding initial data...")
        
        # import models and dependencies with proper error handling
        try:
            from app.models.models import User, Category, MenuItem, SavedAddress, Order, OrderItem, Promocode, ModificationType
            from app.core.security import get_password_hash
            from datetime import datetime, timedelta
            import random
            import json
        except ImportError as e:
            logger.error(f"Import error during seeding: {e}")
            return False
        
        db = SessionLocal()
        try:
            # load real menu data from menu.json
            try:
                menu_json_path = project_root / "menu.json"
                with open(menu_json_path, 'r', encoding='utf-8') as f:
                    menu_data = json.load(f)
                logger.info("Loaded menu data from menu.json")
            except Exception as e:
                logger.error(f"Failed to load menu.json: {e}")
                return False
            
            # create categories from menu.json
            categories = []
            category_names = [category["category"] for category in menu_data["menu"]]
            
            for i, cat_name in enumerate(category_names, 1):
                existing = db.query(Category).filter(Category.name == cat_name).first()
                if not existing:
                    category = Category(
                        name=cat_name,
                        sort=i,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(category)
                    categories.append(category)
                    logger.info(f"Created category: {cat_name}")
                else:
                    categories.append(existing)
            
            db.commit()
            
            # refresh categories to get IDs
            for cat in categories:
                db.refresh(cat)
            
            # create menu items from menu.json
            menu_items = []
            for category_data in menu_data["menu"]:
                category_name = category_data["category"]
                category = next((cat for cat in categories if cat.name == category_name), None)
                
                if category:
                    for item_data in category_data["items"]:
                        existing_item = db.query(MenuItem).filter(
                            MenuItem.name == item_data["name"],
                            MenuItem.category_id == category.id
                        ).first()
                        if not existing_item:
                            # Convert price from kopecks to rubles (divide by 100)
                            price_rubles = item_data["price"] / 100.0
                            menu_item = MenuItem(
                                category_id=category.id,
                                name=item_data["name"],
                                description=item_data["description"],
                                price=price_rubles,
                                is_active=True,
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            db.add(menu_item)
                            menu_items.append(menu_item)
                            logger.info(f"Created menu item: {item_data['name']}")
                        else:
                            menu_items.append(existing_item)
            
            db.commit()
            
            # refresh menu items to get IDs
            for item in menu_items:
                db.refresh(item)
            
            # create default modification types
            logger.info("Creating default modification types...")
            
            # Default sauces (available by default for all dishes)
            default_sauces = [
                {"name": "сырный", "category": "sauce", "is_default": True},
                {"name": "кетчуп", "category": "sauce", "is_default": True},
                {"name": "кисло-сладкий", "category": "sauce", "is_default": True},
                {"name": "ранч", "category": "sauce", "is_default": True},
                {"name": "горчичный", "category": "sauce", "is_default": True},
            ]
            
            # Removal options (things that can be removed from dishes)
            removal_options = [
                {"name": "лука", "category": "removal", "is_default": False},
                {"name": "майонеза", "category": "removal", "is_default": False},
                {"name": "кетчупа", "category": "removal", "is_default": False},
                {"name": "мяса", "category": "removal", "is_default": False},
            ]
            
            all_modifications = default_sauces + removal_options
            
            # Check which modifications already exist
            existing_names = set()
            existing_mods = db.query(ModificationType).all()
            for mod in existing_mods:
                existing_names.add((mod.name, mod.category))
            
            created_count = 0
            for mod_data in all_modifications:
                key = (mod_data["name"], mod_data["category"])
                if key not in existing_names:
                    modification = ModificationType(
                        name=mod_data["name"],
                        category=mod_data["category"],
                        is_default=mod_data["is_default"],
                        is_active=True
                    )
                    db.add(modification)
                    created_count += 1
                    logger.info(f"Created {mod_data['category']} modification: {mod_data['name']}")
                else:
                    logger.info(f"Skipped existing {mod_data['category']} modification: {mod_data['name']}")
            
            if created_count > 0:
                db.commit()
                logger.info(f"Successfully created {created_count} modification types.")
            else:
                logger.info("No new modification types were created (all already exist).")
            
            # Display summary
            total_sauces = db.query(ModificationType).filter(ModificationType.category == "sauce").count()
            total_removals = db.query(ModificationType).filter(ModificationType.category == "removal").count()
            logger.info(f"Database now contains: {total_sauces} sauce modifications, {total_removals} removal modifications")
            
            # create default admin user
            admin_email = "admin@ium.app"
            existing_admin = db.query(User).filter(User.email == admin_email).first()
            
            if not existing_admin:
                admin_user = User(
                    full_name="APPETIT Admin",
                    email=admin_email,
                    phone="+77081234567",
                    password_hash=get_password_hash("Admin123!"),
                    role="admin",
                    is_email_verified=True,
                    is_phone_verified=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(admin_user)
                logger.info(f"Created admin user: {admin_email}")
            
            # create 2 real users with saved addresses
            # Generate random phone for second user
            random_phone = f"+77{random.randint(7000000000, 7999999999)}"
            
            plain_users_data = [
                {
                    "full_name": "Пользователь 1",
                    "email": "1@ium.app",
                    "phone": "+77081255767",
                    "addresses": [
                        {"address_text": "Алматы, ул. Абая 150А, кв. 25", "lat": 43.2220, "lng": 76.8512, "label": "Дом", "is_default": True},
                        {"address_text": "Алматы, пр. Достык 97, офис 312", "lat": 43.2372, "lng": 76.9461, "label": "Работа", "is_default": False}
                    ]
                },
                {
                    "full_name": "Пользователь 2",
                    "email": "2@ium.app",
                    "phone": random_phone,
                    "addresses": [
                        {"address_text": "Алматы, ул. Фурманова 273, кв. 45", "lat": 43.2630, "lng": 76.9428, "label": "Дом", "is_default": True},
                        {"address_text": "Алматы, ул. Казыбек би 36, офис 201", "lat": 43.2511, "lng": 76.9206, "label": "Офис", "is_default": False}
                    ]
                }
            ]
            
            plain_users = []
            for user_data in plain_users_data:
                existing_user = db.query(User).filter(User.email == user_data["email"]).first()
                if not existing_user:
                    user = User(
                        full_name=user_data["full_name"],
                        email=user_data["email"],
                        phone=user_data["phone"],
                        password_hash=get_password_hash("User123!"),
                        role="user",
                        is_email_verified=True,
                        is_phone_verified=True,
                        created_at=datetime.utcnow() - timedelta(days=random.randint(30, 180)),
                        updated_at=datetime.utcnow()
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                    
                    # create saved addresses for each user
                    for addr_data in user_data["addresses"]:
                        address = SavedAddress(
                            user_id=user.id,
                            address_text=addr_data["address_text"],
                            latitude=addr_data["lat"],
                            longitude=addr_data["lng"],
                            label=addr_data["label"],
                            is_default=addr_data["is_default"],
                            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                        )
                        db.add(address)
                    
                    plain_users.append(user)
                    logger.info(f"Created plain user: {user_data['email']} with addresses")
                else:
                    plain_users.append(existing_user)
            
            db.commit()
            
            # create some promocodes for realistic usage
            promo_codes_data = [
                {"code": "WELCOME10", "kind": "percent", "value": 10, "active": True},
                {"code": "SAVE5", "kind": "amount", "value": 5, "active": True},
                {"code": "NEWUSER20", "kind": "percent", "value": 20, "active": True},
            ]
            
            for promo_data in promo_codes_data:
                existing_promo = db.query(Promocode).filter(Promocode.code == promo_data["code"]).first()
                if not existing_promo:
                    promo = Promocode(**promo_data, created_at=datetime.utcnow())
                    db.add(promo)
                    logger.info(f"Created promocode: {promo_data['code']}")
            
            db.commit()
            
            # create 2 orders in each state for each user
            order_states = ["NEW", "COOKING", "ON_WAY", "DELIVERED", "CANCELLED"]
            order_counter = 1000
            
            for user in plain_users:
                user_addresses = db.query(SavedAddress).filter(SavedAddress.user_id == user.id).all()
                if not user_addresses:
                    continue
                
                for state in order_states:
                    for i in range(2):  # 2 orders per state
                        order_counter += 1
                        random_address = random.choice(user_addresses)
                        
                        # create realistic order timing based on status
                        if state == "NEW":
                            created_time = datetime.utcnow() - timedelta(minutes=random.randint(1, 30))
                        elif state == "COOKING":
                            created_time = datetime.utcnow() - timedelta(minutes=random.randint(30, 60))
                        elif state == "ON_WAY":
                            created_time = datetime.utcnow() - timedelta(minutes=random.randint(60, 120))
                        elif state == "DELIVERED":
                            created_time = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                        else:  # CANCELLED
                            created_time = datetime.utcnow() - timedelta(days=random.randint(1, 7))
                        
                        # select random menu items for the order
                        selected_items = random.sample(menu_items, random.randint(2, 4))
                        subtotal = 0
                        
                        order = Order(
                            number=f"ORD-{order_counter}",
                            user_id=user.id,
                            fulfillment=random.choice(["delivery", "pickup"]),
                            address_text=random_address.address_text,
                            lat=random_address.latitude,
                            lng=random_address.longitude,
                            status=state,
                            subtotal=0,  # will calculate below
                            discount=0,
                            total=0,  # will calculate below
                            payment_method=random.choice(["cod", "online"]),
                            paid=(state in ["DELIVERED", "CANCELLED"] or random.choice([True, False])),
                            created_at=created_time
                        )
                        db.add(order)
                        db.flush()  # Get ID without committing
                        
                        # create order items
                        for menu_item in selected_items:
                            qty = random.randint(1, 3)
                            price = float(menu_item.price)
                            subtotal += qty * price
                            
                            order_item = OrderItem(
                                order_id=order.id,
                                item_id=menu_item.id,
                                name_snapshot=menu_item.name,
                                qty=qty,
                                price_at_moment=price
                            )
                            db.add(order_item)
                        
                        # update order totals
                        order.subtotal = subtotal
                        order.total = subtotal
                        db.add(order)
                        
                        logger.info(f"Created {state} order {order.number} for {user.email}")
            
            db.commit()
            logger.info("Enhanced data seeded successfully with users, addresses, menu items, and orders")
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