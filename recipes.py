import os
import re
import requests
from dotenv import load_dotenv
from slugify import slugify

load_dotenv()
SPOON_KEY = os.getenv("SPOONACULAR_API_KEY")

# Very light normalization for units and names
UNIT_ALIASES = {
    "tsp": ["tsp", "teaspoon", "teaspoons"],
    "tbsp": ["tbsp", "tablespoon", "tablespoons"],
    "cup": ["cup", "cups"],
    "oz": ["oz", "ounce", "ounces"],
    "lb": ["lb", "lbs", "pound", "pounds"],
    "g": ["g", "gram", "grams"],
    "kg": ["kg", "kilogram", "kilograms"],
    "ml": ["ml", "milliliter", "milliliters"],
    "l": ["l", "liter", "liters"],
}

def canonical_unit(token: str | None):
    if not token:
        return None
    t = token.lower().strip()
    for canon, variants in UNIT_ALIASES.items():
        if t in variants:
            return canon
    return t  # leave as-is if unknown

def canonical_name(name: str):
    # Lowercase, remove extra punctuation, crude lemmatization for plural 's'
    n = name.strip().lower()
    n = re.sub(r"[^\w\s\-]", "", n)
    n = re.sub(r"\s+", " ", n)
    if n.endswith("es") and len(n) > 3:
        if n.endswith("ies"):
            n = n[:-3] + "y"   # berries -> berry
        else:
            n = n[:-2]          # tomatoes -> tomato
    elif n.endswith("s") and len(n) > 3:
        n = n[:-1]              # carrots -> carrot
    return n

def parse_quantity_unit(text: str):
    """
    Try to pull quantity + unit from a line like:
    "2 cups chopped tomatoes" -> qty=2, unit=cup, name="chopped tomatoes"
    "1.5 lb ground beef" -> qty=1.5, unit=lb, name="ground beef"
    "tomato" -> qty=None, unit=None, name="tomato"
    """
    t = text.strip()
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s+([a-zA-Z]+)\s+(.*)$", t)
    if m:
        qty = float(m.group(1))
        unit = canonical_unit(m.group(2))
        name = canonical_name(m.group(3))
        return qty, unit, name
    m2 = re.match(r"^\s*(\d+(?:\.\d+)?)\s+(.*)$", t)
    if m2:
        qty = float(m2.group(1))
        unit = None
        name = canonical_name(m2.group(2))
        return qty, unit, name
    # fallback: no qty/unit
    return None, None, canonical_name(t)

# -------- Spoonacular by URL (optional) --------
def spoonacular_from_url(url: str):
    """
    Given a recipe URL, use Spoonacular to extract ingredients.
    Requires SPOONACULAR_API_KEY in your .env
    """
    if not SPOON_KEY:
        raise RuntimeError("SPOONACULAR_API_KEY not set")
    # 1) Find recipe id from URL
    info = requests.get(
        "https://api.spoonacular.com/recipes/extract",
        params={"apiKey": SPOON_KEY, "url": url}
    ).json()

    title = info.get("title") or "Untitled Recipe"
    ingredients = []
    for ing in info.get("extendedIngredients", []):
        qty = ing.get("measures", {}).get("metric", {}).get("amount") or ing.get("amount")
        unit = ing.get("measures", {}).get("metric", {}).get("unitShort") or ing.get("unit")
        name = ing.get("name") or ""
        # Normalize
        q = float(qty) if isinstance(qty, (int, float, str)) and str(qty).replace(".","",1).isdigit() else None
        ingredients.append({
            "name": canonical_name(name),
            "quantity": q or 1.0,
            "unit": canonical_unit(unit),
        })

    return {
        "title": title.strip(),
        "source_url": url,
        "ingredients": ingredients,
    }

# -------- Paste-a-list (no API) --------
def parse_pasted_ingredients(title: str, raw_text: str):
    """
    raw_text: lines like:
      2 cups spinach
      1 lb chicken breast
      3 tomatoes
      salt
    """
    ingredients = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        qty, unit, name = parse_quantity_unit(line)
        ingredients.append({
            "name": name,
            "quantity": float(qty) if qty is not None else 1.0,
            "unit": canonical_unit(unit),
        })

    return {
        "title": title.strip() or "Untitled Recipe",
        "source_url": None,
        "ingredients": ingredients,
    }
