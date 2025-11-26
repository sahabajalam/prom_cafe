from .database import SessionLocal, engine
from . import models
from sqlalchemy import text

def clear_data():
    db = SessionLocal()
    try:
        # Truncate tables to clear data but keep schema
        # Using CASCADE to handle foreign keys if any (though we don't have strict FK constraints on ingredients yet)
        db.execute(text("TRUNCATE TABLE menu_items, ingredients, item_ingredients RESTART IDENTITY CASCADE;"))
        db.commit()
        print("Database cleared.")
    except Exception as e:
        print(f"Error clearing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_data()
