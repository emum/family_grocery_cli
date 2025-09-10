import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, String, Boolean, DateTime, Float, ForeignKey, text, select, delete, update
)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in .env")

engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()

# --- Tables ---
grocery_items = Table(
    "grocery_items",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(200), nullable=False),
    Column("purchased", Boolean, nullable=False, default=False),
    Column("added_at", DateTime, nullable=False, default=datetime.utcnow),
    # NEW in Week 6:
    Column("quantity", Float, nullable=False, server_default=text("1")),
    Column("unit", String(50), nullable=True),
)

recipes = Table(
    "recipes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(300), nullable=False),
    Column("source_url", String(1000), nullable=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)

recipe_ingredients = Table(
    "recipe_ingredients",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("recipe_id", Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
    Column("name", String(200), nullable=False),
    Column("quantity", Float, nullable=False, server_default=text("1")),
    Column("unit", String(50), nullable=True),
)

def init_db():
    # Create tables if they don't exist
    metadata.create_all(engine)
    # Ensure new columns exist (safe on Postgres)
    with engine.begin() as conn:
        conn.execute(text("""
            ALTER TABLE grocery_items
            ADD COLUMN IF NOT EXISTS quantity DOUBLE PRECISION DEFAULT 1
        """))
        conn.execute(text("""
            ALTER TABLE grocery_items
            ADD COLUMN IF NOT EXISTS unit VARCHAR(50)
        """))

# --- Queries used by the CLI ---
def list_items():
    stmt = select(grocery_items).order_by(grocery_items.c.purchased.asc(),
                                          grocery_items.c.name.asc())
    with engine.begin() as conn:
        rows = conn.execute(stmt).mappings().all()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "purchased": r["purchased"],
            "added_at": r["added_at"].strftime("%Y-%m-%d %H:%M"),
            "quantity": r["quantity"] or 1,
            "unit": r["unit"],
        } for r in rows
    ]

def add_item(name: str, quantity: float = 1.0, unit: str | None = None):
    # Merge with existing unpurchased same-name+unit item by increasing quantity
    with engine.begin() as conn:
        # Build the unit-matching predicate depending on Python value of `unit`
        if unit is None:
            unit_pred = grocery_items.c.unit.is_(None)
        else:
            unit_pred = grocery_items.c.unit == unit

        existing = conn.execute(
            select(grocery_items.c.id, grocery_items.c.quantity)
            .where(grocery_items.c.name.ilike(name))
            .where(unit_pred)
            .where(grocery_items.c.purchased == False)
        ).mappings().first()

        new_qty = float(quantity or 1)

        if existing:
            conn.execute(
                update(grocery_items)
                .where(grocery_items.c.id == existing["id"])
                .values(quantity=(existing["quantity"] or 1) + new_qty)
            )
        else:
            conn.execute(grocery_items.insert().values(
                name=name,
                purchased=False,
                added_at=datetime.utcnow(),
                quantity=new_qty,
                unit=unit
            ))

def remove_item(item_id: int):
    with engine.begin() as conn:
        conn.execute(delete(grocery_items).where(grocery_items.c.id == item_id))

def toggle_purchased(item_id: int):
    with engine.begin() as conn:
        # flip bool in DB
        conn.execute(update(grocery_items)
                     .where(grocery_items.c.id == item_id)
                     .values(purchased=~grocery_items.c.purchased))

# --- Recipe helpers ---
def create_recipe(title: str, source_url: str | None, ingredients: list[dict]) -> int:
    """
    ingredients: list of {name, quantity (float), unit (str|None)}
    Returns new recipe_id
    """
    with engine.begin() as conn:
        rid = conn.execute(
            recipes.insert().values(title=title, source_url=source_url, created_at=datetime.utcnow())
        ).inserted_primary_key[0]
        if ingredients:
            conn.execute(recipe_ingredients.insert(), [
                {"recipe_id": rid, "name": ing["name"], "quantity": float(ing.get("quantity") or 1), "unit": ing.get("unit")}
                for ing in ingredients
            ])
        return rid

def get_recipe(recipe_id: int):
    with engine.begin() as conn:
        r = conn.execute(select(recipes).where(recipes.c.id == recipe_id)).mappings().first()
        if not r:
            return None
        ings = conn.execute(select(recipe_ingredients)
                            .where(recipe_ingredients.c.recipe_id == recipe_id)
                            .order_by(recipe_ingredients.c.name.asc())).mappings().all()
        return {
            "id": r["id"],
            "title": r["title"],
            "source_url": r["source_url"],
            "ingredients": [{"name": i["name"], "quantity": i["quantity"], "unit": i["unit"]} for i in ings]
        }

def add_recipe_to_grocery(recipe_id: int):
    rec = get_recipe(recipe_id)
    if not rec:
        return False
    for ing in rec["ingredients"]:
        add_item(ing["name"], ing.get("quantity", 1) or 1, ing.get("unit"))
    return True
