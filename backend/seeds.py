from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models

def seed_data(force: bool = False):
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if data exists and is sufficient
    item_count = db.query(models.MenuItem).count()
    if item_count > 50:
        if force:
            print("Forcing re-seed: Deleting existing items...")
            db.query(models.MenuItem).delete()
            db.commit()
        else:
            print(f"Data already exists ({item_count} items). Skipping seed.")
            db.close()
            return
    elif item_count > 0:
        print(f"Partial data detected ({item_count} items). Clearing and re-seeding...")
        db.query(models.MenuItem).delete()
        db.commit()

    # Ingredients (simplified for now, extracting unique allergens from PDF logic would be complex here)
    # We will just store allergens in the menu item or ingredient text for now.
    
    # Menu Items from PDF (Full List)
    from .parse_menu import parse_structured
    items = parse_structured()

    for item_data in items:
        db_item = models.MenuItem(**item_data)
        db.add(db_item)
    
    db.commit()
    print("Database seeded successfully.")
    db.close()

if __name__ == "__main__":
    seed_data()
