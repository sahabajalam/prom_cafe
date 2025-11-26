from backend.database import SessionLocal
from backend.models import MenuItem

db = SessionLocal()
items = db.query(MenuItem).all()
categories = sorted(list(set(item.category for item in items if item.category)))
print("Categories found:")
for cat in categories:
    print(f"'{cat}'")
db.close()
