import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import select, delete, update
from sqlalchemy.engine.url import make_url

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in .env")

# Create engine
engine = create_engine(DATABASE_URL, future=True)

# Define schema (Month 2, Week 5 level)
metadata = MetaData()
grocery_items = Table(
    "grocery_items",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(200), nullable=False),
    Column("purchased", Boolean, nullable=False, default=False),
    Column("added_at", DateTime, nullable=False, default=datetime.utcnow),
)

def init_db():
    metadata.create_all(engine)

def list_items():
    # Unpurchased first, then by name (matches your CLI’s default)
    stmt = select(grocery_items).order_by(grocery_items.c.purchased.asc(),
                                          grocery_items.c.name.asc())
    with engine.begin() as conn:
        rows = conn.execute(stmt).mappings().all()
    # Convert to CLI’s dict shape
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "purchased": r["purchased"],
            "added_at": r["added_at"].strftime("%Y-%m-%d %H:%M"),
        } for r in rows
    ]

def add_item(name: str):
    with engine.begin() as conn:
        conn.execute(grocery_items.insert().values(
            name=name, purchased=False, added_at=datetime.utcnow()
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
