import re
import json

def parse_menu_dump(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    items = []
    current_item = {}
    
    # Regex patterns
    price_pattern = r"£(\d+\.\d+)"
    
    # Simple state machine
    # We look for lines that start with a price or look like an item name
    
    # This is a heuristic parser based on the observed format
    # "Item Name Price Description Contains May Contain / Notes"
    
    # Let's try to identify blocks.
    # Usually: Name -> Price/Desc -> Allergens -> Notes
    
    buffer = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip headers
        if "Item Name Price" in line:
            continue
            
        # Detect price line (often starts with £ or contains it early)
        price_match = re.search(price_pattern, line)
        
        if price_match:
            # If we have a price, it's likely the start of a new item OR the description line of the previous item name
            # Looking at the dump:
            # 109: Full English Breakfast 
            # 110: £12.95 2 pork sausages...
            
            # So if we have a buffer, the buffer is likely the Name.
            if buffer:
                name = " ".join(buffer).strip()
                current_item = {"name": name}
                buffer = []
                
                # Extract price
                current_item["price"] = float(price_match.group(1))
                
                # Description is often on the same line as price, after the price
                # "£12.95 2 pork sausages..."
                desc_part = line.split(price_match.group(0), 1)[1].strip()
                current_item["description"] = desc_part
                
                items.append(current_item)
            else:
                # Price line without a preceding name buffer? 
                # Maybe the name was on the same line? "Bacon Bap £6.00 Served..."
                # Let's handle that case if needed, but the dump seems to split them often.
                pass
        
        elif "Contains" in line or "Gluten" in line or "Milk" in line:
             # Likely allergen line
             if items:
                 items[-1]["dietary_tags"] = line # Store raw string for now
        
        elif "May contain" in line or "Notes" in line or "ALERT" in line:
            if items:
                items[-1]["may_contain"] = line
        
        else:
            # Just text, maybe name?
            buffer.append(line)

    return items

# Since the dump is messy, let's try a more robust approach using the line numbers from the view_file output as a guide
# 109: Full English Breakfast 
# 110: £12.95 ...
# 111: Gluten...
# 112: Soya...

def parse_structured():
    items = []
    
    # Manual extraction based on reading the file content provided in history
    # This is safer than writing a complex parser for a one-off messy text file
    
    raw_data = [
        {"name": "Full English Breakfast", "price": 12.95, "description": "2 pork sausages, 2 bacon, 1 hash brown, 1 fried egg, beans, tomato, toast.", "category": "Breakfast", "dietary_tags": "Gluten, Eggs, Soya, Sulphur Dioxide", "safety_alerts": "Soya is in the bread; Sulphur is in the sausage."},
        {"name": "Vegetarian Breakfast", "price": 12.50, "description": "2 vegan sausages, 2 hash browns, 2 fried eggs, beans, tomato, toast.", "category": "Breakfast", "dietary_tags": "Gluten, Eggs, Celery, Soya (V)", "safety_alerts": "Celery is in the Veggie Sausage."},
        {"name": "Vegan Breakfast", "price": 12.50, "description": "Vegan sausage, hash browns, beans, tomato, toast.", "category": "Breakfast", "dietary_tags": "Gluten, Celery, Soya, Sesame (VG)", "safety_alerts": "Sesame was listed on the specific 'Vegan Toast' sheet."},
        {"name": "Sausage Bap", "price": 6.00, "description": "Served in a floured bun.", "category": "Breakfast", "dietary_tags": "Gluten, Sulphur Dioxide", "may_contain": "Sesame (Bun)"},
        {"name": "Vegan Sausage Bap", "price": 6.00, "description": "Served in a floured bun.", "category": "Breakfast", "dietary_tags": "Gluten, Celery (VG)", "may_contain": "Sesame (Bun)"},
        {"name": "Bacon Bap", "price": 6.00, "description": "Served in a floured bun.", "category": "Breakfast", "dietary_tags": "Gluten", "may_contain": "Sesame (Bun)"},
        {"name": "Pastries", "price": 2.75, "description": "Croissant or Pain au Chocolat.", "category": "Breakfast", "dietary_tags": "Gluten, Eggs, Milk, Soya", "may_contain": "Nuts (Almond/Hazelnut)"},
        
        {"name": "Chips", "price": 4.50, "description": "Thick cut chips.", "category": "Sides", "dietary_tags": "None Listed (V, VG)", "safety_alerts": "Check cross-contamination."},
        {"name": "Cheesy Chips", "price": 5.50, "description": "Chips topped with cheese.", "category": "Sides", "dietary_tags": "Milk (V)"},
        {"name": "Jumbo Sausage Roll", "price": 4.00, "description": "Puff pastry sausage roll.", "category": "Snacks", "dietary_tags": "Gluten, Eggs, Milk"},
        {"name": "Hot Dog", "price": 4.90, "description": "Frankfurter with crispy onions.", "category": "Snacks", "dietary_tags": "Gluten", "may_contain": "Sesame, Soya"},
        {"name": "Phat Pasty (Traditional)", "price": 5.60, "description": "Traditional Cornish pasty.", "category": "Snacks", "dietary_tags": "Gluten, Eggs", "may_contain": "Milk"},
        {"name": "Phat Pasty (Vegan)", "price": 5.60, "description": "Vegan Keralan/Curry pasty.", "category": "Snacks", "dietary_tags": "Gluten (VG)"},
        {"name": "Phat Pasty (Cheese)", "price": 5.60, "description": "Cheese & Onion / Cheese & Bacon.", "category": "Snacks", "dietary_tags": "Gluten, Eggs, Milk, Mustard"},
        
        {"name": "Cod Goujons", "price": 7.50, "description": "Served with chips & beans.", "category": "Kids", "dietary_tags": "Gluten, Fish, Mustard"},
        {"name": "Chicken Bites", "price": 7.50, "description": "Served with chips & beans.", "category": "Kids", "dietary_tags": "Gluten"},
        {"name": "Pork Sausage", "price": 7.50, "description": "Served with chips & beans.", "category": "Kids", "dietary_tags": "Gluten, Sulphur Dioxide"},
        {"name": "Veggie Sausage", "price": 7.50, "description": "Served with chips & beans.", "category": "Kids", "dietary_tags": "Gluten, Celery"},
        
        {"name": "Cod & Chips", "price": 14.95, "description": "Hand battered fish, lemon, mushy peas, chips.", "category": "Mains", "dietary_tags": "Gluten, Fish"},
        {"name": "Gourmet Beef Burger", "price": 12.50, "description": "Brioche bun, lettuce, tomato, chips.", "category": "Mains", "dietary_tags": "Gluten, Eggs, Milk", "may_contain": "Sesame (Bun)"},
        {"name": "Buttermilk Chicken Burger", "price": 13.00, "description": "Brioche bun, lettuce, tomato, chips.", "category": "Mains", "dietary_tags": "Gluten, Eggs, Milk", "may_contain": "Sesame, Celery, Mustard, Soya"},
        {"name": "Vegan Spicy Bean Burger", "price": 13.00, "description": "Floured bap, lettuce, tomato, chips.", "category": "Mains", "dietary_tags": "Gluten (VG)", "may_contain": "Sesame"},
        {"name": "Bacon Cheese Burger", "price": 14.00, "description": "Brioche bun, lettuce, tomato, chips.", "category": "Mains", "dietary_tags": "Gluten, Eggs, Milk", "may_contain": "Sesame, Celery, Mustard, Soya"},
        
        {"name": "Plain Jacket", "price": 5.50, "description": "Butter/Spread.", "category": "Jackets", "dietary_tags": "Milk"},
        {"name": "Jacket + Beans or Cheese", "price": 7.10, "description": "Beans / Cheddar.", "category": "Jackets", "dietary_tags": "Milk (Cheese)"},
        {"name": "Jacket + Chilli Con Carne", "price": 7.80, "description": "Beef Chilli.", "category": "Jackets", "dietary_tags": "Celery, Mustard, Sulphur", "may_contain": "Soya"},
        {"name": "Jacket + Vegan Chilli", "price": 7.80, "description": "Three bean chilli.", "category": "Jackets", "dietary_tags": "Celery, Gluten", "may_contain": "Mustard, Soya, Sulphur"},
        {"name": "Jacket + Tuna Mayo", "price": 7.80, "description": "Tuna Mayonnaise.", "category": "Jackets", "dietary_tags": "Eggs, Fish, Mustard"},
        
        {"name": "Chicken & Pesto Toastie", "price": 7.50, "description": "Chicken, cheese, pesto.", "category": "Toasties", "dietary_tags": "Gluten, Milk", "may_contain": "Soya"},
        {"name": "Tuna Melt Toastie", "price": 7.50, "description": "Tuna, mozzarella, red onion.", "category": "Toasties", "dietary_tags": "Gluten, Fish, Milk"},
        {"name": "Ham & Cheese Toastie", "price": 7.50, "description": "Smoked ham, cheddar.", "category": "Toasties", "dietary_tags": "Gluten, Milk"},
        {"name": "Mozzarella & Tomato Toastie", "price": 7.50, "description": "Pesto, sun-dried tomato.", "category": "Toasties", "dietary_tags": "Gluten, Milk"},
        {"name": "Sourdough Toastie", "price": 7.50, "description": "Ham, Edam, Dijonnaise.", "category": "Toasties", "dietary_tags": "Gluten, Milk", "safety_alerts": "MISSING DATA: No sheet found for 'Dijonnaise'. Assume Mustard & Egg."},
        
        {"name": "Tuna Mayo Sandwich", "price": 6.90, "description": "Meal Deal Option.", "category": "Sandwiches", "dietary_tags": "Gluten, Eggs, Fish, Mustard, Soya"},
        {"name": "BLT Sandwich", "price": 6.90, "description": "Meal Deal Option.", "category": "Sandwiches", "dietary_tags": "Gluten, Milk, Soya"},
        {"name": "Cheese Sandwich", "price": 6.90, "description": "Meal Deal Option.", "category": "Sandwiches", "dietary_tags": "Gluten, Milk, Soya, Sulphur"},
        {"name": "Coronation Chicken Sandwich", "price": 6.90, "description": "Meal Deal Option.", "category": "Sandwiches", "dietary_tags": "Gluten, Eggs, Milk, Mustard, Soya, Sulphur"},
        
        {"name": "Fruit Scone", "price": 4.70, "description": "With butter & jam.", "category": "Cakes", "dietary_tags": "Gluten, Milk, Sulphur Dioxide"},
        {"name": "Cream Tea", "price": 7.50, "description": "Scone, jam, clotted cream, tea.", "category": "Cakes", "dietary_tags": "Gluten, Milk, Sulphur Dioxide"},
        {"name": "Toasted Teacake", "price": 2.60, "description": "Spiced fruit bun.", "category": "Cakes", "dietary_tags": "Gluten, Milk", "may_contain": "Soya"},
        {"name": "Victoria/Lemon Sponge", "price": 4.60, "description": "Homemade Sponge.", "category": "Cakes", "dietary_tags": "Gluten, Eggs, Milk"},
        {"name": "Coffee & Walnut Cake", "price": 4.60, "description": "Homemade Sponge.", "category": "Cakes", "dietary_tags": "Gluten, Eggs, Milk, NUTS", "safety_alerts": "NUT ALERT: Your sheet missed the 'Nut' tickbox. I have manually added Nuts."},
        {"name": "Tray Bakes", "price": 4.10, "description": "Brownies, Flapjacks, etc.", "category": "Cakes", "dietary_tags": "Gluten, Eggs, Milk, Soya"},
        {"name": "Muffins", "price": 3.50, "description": "Blueberry, Choc, etc.", "category": "Cakes", "dietary_tags": "Gluten, Eggs, Milk, Soya", "may_contain": "Nuts"},
        
        {"name": "Scoop Ice Cream", "price": 3.90, "description": "New Forest Scoops.", "category": "Ice Cream", "dietary_tags": "Milk", "safety_alerts": "Cookie Dough/Brownie flavors: Add Gluten/Soya."},
        {"name": "Magnum", "price": 3.50, "description": "Classic/White/Mint.", "category": "Ice Cream", "dietary_tags": "Milk", "safety_alerts": "Billionaire/Starchaser: Add Gluten."},
        {"name": "Cornetto Classico", "price": 3.00, "description": "Var.", "category": "Ice Cream", "dietary_tags": "Gluten, Milk, NUTS (Hazelnuts)"},
        {"name": "Cornetto Strawberry", "price": 3.00, "description": "Var.", "category": "Ice Cream", "dietary_tags": "Gluten, Milk"},
        {"name": "Feast", "price": 3.00, "description": "Var.", "category": "Ice Cream", "dietary_tags": "Milk", "may_contain": "Peanuts/Nuts"},
        {"name": "Soft Serve (Whippy)", "price": 3.00, "description": "In Cone.", "category": "Ice Cream", "dietary_tags": "Gluten, Milk, Soya"},
        
        {"name": "Americano / Espresso", "price": 3.40, "description": "Black coffee.", "category": "Drinks", "dietary_tags": "None Listed"},
        {"name": "Latte / Cappuccino", "price": 3.70, "description": "With Cows Milk.", "category": "Drinks", "dietary_tags": "Milk"},
        {"name": "Hot Chocolate / Mocha", "price": 3.70, "description": "With Cows Milk.", "category": "Drinks", "dietary_tags": "Milk, Soya"},
        {"name": "Oat Milk", "price": 0.60, "description": "Alternative.", "category": "Drinks", "dietary_tags": "Gluten", "safety_alerts": "ALERT: Unless bottle says 'Gluten Free', Oat milk contains Gluten."},
        {"name": "Almond Milk", "price": 0.60, "description": "Alternative.", "category": "Drinks", "dietary_tags": "Nuts (Almonds)"},
        {"name": "Hazelnut Syrup", "price": 0.60, "description": "Syrup Shot.", "category": "Drinks", "dietary_tags": "Nuts (Hazelnut)"},
        {"name": "Jimmy's Iced Coffee", "price": 4.90, "description": "Carton/Can.", "category": "Drinks", "dietary_tags": "Milk"},
        {"name": "Milkshakes", "price": 4.90, "description": "Powder + Milk/Cream.", "category": "Drinks", "dietary_tags": "Milk"},
        {"name": "Tropical Ice", "price": 4.90, "description": "Slush.", "category": "Drinks", "dietary_tags": "None Listed"},
        
        # Critical Conflict Item
        {"name": "Vegan Chicken Burger", "price": 0.0, "description": "The menu lists this as 'Vegan', but allergen sheet lists Brioche Bun containing Egg and Milk.", "category": "Mains", "dietary_tags": "NOT VEGAN", "safety_alerts": "CRITICAL: This dish is NOT VEGAN as currently documented. Brioche Bun contains Egg and Milk."}
    ]
    return raw_data

if __name__ == "__main__":
    items = parse_structured()
    print(json.dumps(items, indent=2))
