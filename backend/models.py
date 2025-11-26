from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Text, Boolean
from sqlalchemy.orm import relationship
from .database import Base

item_ingredients = Table(
    "item_ingredients",
    Base.metadata,
    Column("menu_item_id", Integer, ForeignKey("menu_items.id")),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id")),
)

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    category = Column(String, index=True)
    dietary_tags = Column(String) # Comma separated tags: V, VG, GF, etc.
    prep_time = Column(Integer, nullable=True)
    
    # Safety fields from PDF
    safety_alerts = Column(Text, nullable=True) # Critical alerts like "NOT VEGAN"
    may_contain = Column(Text, nullable=True) # "May contain: Sesame"

    ingredients = relationship("Ingredient", secondary=item_ingredients, back_populates="menu_items")

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    allergens = Column(String) # Comma separated: Gluten, Dairy, etc.
    is_halal = Column(Boolean, default=True)

    menu_items = relationship("MenuItem", secondary=item_ingredients, back_populates="ingredients")
