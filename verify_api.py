import requests
from collections import Counter

try:
    response = requests.get("http://127.0.0.1:8000/menu/")
    response.raise_for_status()
    items = response.json()
    
    print(f"Total items fetched: {len(items)}")
    
    categories = Counter(item['category'] for item in items)
    print("\nItems per Category:")
    for cat, count in categories.items():
        print(f"{cat}: {count}")
        
except Exception as e:
    print(f"Error: {e}")
