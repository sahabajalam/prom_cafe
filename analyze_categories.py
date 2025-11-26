from backend.database import SessionLocal
from backend.models import MenuItem
from sqlalchemy import func

db = SessionLocal()
results = db.query(MenuItem.category, func.count(MenuItem.id)).group_by(MenuItem.category).all()

print("--- START REPORT ---")
for category, count in results:
    print(f"{category}: {count}")
print("--- END REPORT ---")

db.close()
