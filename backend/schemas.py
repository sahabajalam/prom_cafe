from pydantic import BaseModel
from typing import List, Optional

class IngredientBase(BaseModel):
    name: str
    allergens: Optional[str] = None
    is_halal: bool = True

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int

    class Config:
        from_attributes = True

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    dietary_tags: Optional[str] = None
    prep_time: Optional[int] = None
    safety_alerts: Optional[str] = None
    may_contain: Optional[str] = None

class MenuItemCreate(MenuItemBase):
    pass

class MenuItem(MenuItemBase):
    id: int
    ingredients: List[Ingredient] = []

    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    items: List[MenuItem]
    answer: Optional[str] = None
