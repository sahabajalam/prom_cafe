from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from . import models, schemas, database, seeds

# Load environment variables
load_dotenv()

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Flavorly API")

@app.on_event("startup")
def on_startup():
    seeds.seed_data()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/seed_db")
def seed_database(force: bool = False, db: Session = Depends(get_db)):
    try:
        seeds.seed_data(force=force)
        return {"message": "Database seeded successfully", "force": force}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    count = db.query(models.MenuItem).count()
    return {"status": "healthy", "item_count": count}

@app.get("/menu/", response_model=List[schemas.MenuItem])
def read_menu_items(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    items = db.query(models.MenuItem).offset(skip).limit(limit).all()
    return items

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-2.0-flash')

@app.get("/menu/search/", response_model=schemas.SearchResponse)
def search_menu_items(q: str, db: Session = Depends(get_db)):
    # Fetch all items to provide context to Gemini
    all_items = db.query(models.MenuItem).all()
    
    # Create a simplified representation
    menu_context = []
    for item in all_items:
        menu_context.append({
            "id": item.id,
            "name": item.name,
            "desc": item.description,
            "price": item.price,
            "tags": item.dietary_tags,
            "allergens": item.may_contain
        })
    
    prompt = f"""
    You are a helpful waiter at Prom Cafe. 
    Here is the menu: {json.dumps(menu_context)}
    
    The customer asks: "{q}"
    
    Task: 
    1. Identify the menu items that best match the request.
    2. If the user asks for a meal plan or suggestion, select specific items.
    3. If the user specifies a quantity (e.g. "3 people" or "3 breakfasts"), assume they want that quantity for ALL requested items (like drinks) unless they say otherwise.
    4. Handle mixed dietary requests (e.g. "3 meals, one vegan"). Select items that satisfy EACH person's requirement.
    5. Provide a structured answer listing the selected items. Consolidate duplicates.
       Format:
       [Quantity] x [Item Name] @ £[Unit Price] = £[Line Total]
       
       Total: £[Total Price]
       
       (You can add a brief friendly sentence before or after if appropriate).
    
    Return a JSON object with two keys:
    - "ids": Array of integers (IDs of matched items).
    - "answer": String (Your structured response).
    
    Example: {{ "ids": [1], "answer": "Three Full English Breakfasts would cost £38.85." }}
    """
    
    try:
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        print(f"Gemini Response: {text_response}")
        
        # Robust JSON extraction
        try:
            # Find the first { and last }
            start_idx = text_response.find('{')
            end_idx = text_response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = text_response[start_idx:end_idx+1]
                data = json.loads(json_str)
            else:
                # Try parsing as list if it returned just a list
                start_idx_list = text_response.find('[')
                end_idx_list = text_response.rfind(']')
                if start_idx_list != -1 and end_idx_list != -1:
                     json_str = text_response[start_idx_list:end_idx_list+1]
                     ids = json.loads(json_str)
                     data = {"ids": ids, "answer": "Here are some suggestions."}
                else:
                    raise ValueError("No JSON found")

            matched_ids = data.get("ids", [])
            answer = data.get("answer", "")
            
            # Ensure IDs are integers
            matched_ids = [int(id) for id in matched_ids if isinstance(id, (int, str)) and str(id).isdigit()]
            
            results = []
            if matched_ids:
                results = db.query(models.MenuItem).filter(models.MenuItem.id.in_(matched_ids)).all()
                
            return schemas.SearchResponse(items=results, answer=answer)

        except json.JSONDecodeError:
            print("Failed to parse JSON from AI response")
            return schemas.SearchResponse(items=[], answer="I found some items but couldn't process them perfectly. Please try again.")
            
    except Exception as e:
        print(f"AI Search Error: {e}")
        # Fallback
        items = db.query(models.MenuItem).filter(
            models.MenuItem.name.ilike(f"%{q}%") | 
            models.MenuItem.description.ilike(f"%{q}%")
        ).all()
        return schemas.SearchResponse(items=items, answer=f"AI Error: {str(e)}")

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')
