from db import (
    init_db, list_items as db_list_items, add_item as db_add_item,
    remove_item as db_remove_item, toggle_purchased as db_toggle_purchased,
    create_recipe, add_recipe_to_grocery,
    add_pantry_item, list_pantry_items, get_expiring_items
)
from recipes import spoonacular_from_url, parse_pasted_ingredients

SORT_MODE = "name"

def show_list():
    items = db_list_items()
    if not items:
        print("\nYour grocery list is empty.\n")
        return items
    print("\nGrocery List (auto-sorted: unpurchased first; by " + SORT_MODE + "):")
    for i, item in enumerate(items, 1):
        box = "☑" if item["purchased"] else "☐"
        qty_unit = f"{item['quantity']:.2f}".rstrip("0").rstrip(".")
        if item.get("unit"):
            qty_unit += f" {item['unit']}"
        print(f"{i}. {box} {item['name']}  —  {qty_unit}  —  added {item['added_at']}")
    print()
    return items

def add_item():
    name = input("Enter item to add: ").strip()
    if not name:
        print("No item entered.")
        return
    qty = input("Quantity (default 1): ").strip()
    unit = input("Unit (optional): ").strip() or None
    try:
        q = float(qty) if qty else 1.0
    except ValueError:
        q = 1.0
    db_add_item(name, q, unit)
    print(f"Added: {name}")

def remove_item():
    items = show_list()
    if not items:
        return
    try:
        num = int(input("Enter number of item to remove: "))
        if 1 <= num <= len(items):
            db_remove_item(items[num - 1]["id"])
            print(f"Removed: {items[num - 1]['name']}")
        else:
            print("Invalid number.")
    except ValueError:
        print("Please enter a valid number.")

def toggle_purchased():
    items = show_list()
    if not items:
        return
    try:
        num = int(input("Enter number of item to toggle purchased: "))
        if 1 <= num <= len(items):
            db_toggle_purchased(items[num - 1]["id"])
            state = "purchased" if not items[num - 1]["purchased"] else "not purchased"
            print(f"Toggled '{items[num - 1]['name']}' to {state}.")
        else:
            print("Invalid number.")
    except ValueError:
        print("Please enter a valid number.")

def add_recipe_from_url():
    url = input("Paste recipe URL: ").strip()
    if not url:
        print("No URL provided.")
        return
    try:
        data = spoonacular_from_url(url)
    except Exception as e:
        print(f"Error fetching recipe: {e}")
        return
    rid = create_recipe(data["title"], data["source_url"], data["ingredients"])
    add_recipe_to_grocery(rid)
    print(f"Added '{data['title']}' ingredients to grocery list.")

def add_recipe_by_paste():
    title = input("Recipe title: ").strip()
    print("Paste ingredients (one per line). Finish with an empty line:")
    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)
    data = parse_pasted_ingredients(title, "\n".join(lines))
    rid = create_recipe(data["title"], data["source_url"], data["ingredients"])
    add_recipe_to_grocery(rid)
    print(f"Added '{data['title']}' ingredients to grocery list.")

def pantry_menu():
    while True:
        print("\n=== Pantry Menu ===")
        print("1. Show pantry items")
        print("2. Add pantry item")
        print("3. Show expiring soon")
        print("4. Back to main menu")
        choice = input("Choose: ").strip()

        if choice == "1":
            items = list_pantry_items()
            if not items:
                print("Pantry is empty.")
            else:
                for i, item in enumerate(items, 1):
                    exp = f" (expires {item['expires_at']})" if item['expires_at'] else ""
                    unit = f" {item['unit']}" if item['unit'] else ""
                    print(f"{i}. {item['name']} — {item['quantity']}{unit}{exp}")
        elif choice == "2":
            name = input("Item name: ").strip()
            qty = input("Quantity (default 1): ").strip()
            unit = input("Unit (optional): ").strip() or None
            exp = input("Expiration date (YYYY-MM-DD, optional): ").strip() or None
            try:
                q = float(qty) if qty else 1.0
            except ValueError:
                q = 1.0
            add_pantry_item(name, q, unit, exp)
            print(f"Added {name} to pantry.")
        elif choice == "3":
            days = input("Show items expiring within how many days? (default 3): ").strip()
            try:
                d = int(days) if days else 3
            except ValueError:
                d = 3
            expiring = get_expiring_items(d)
            if not expiring:
                print(f"No items expiring in {d} days.")
            else:
                print(f"Items expiring in {d} days:")
                for e in expiring:
                    unit = f" {e['unit']}" if e['unit'] else ""
                    print(f"- {e['name']} — {e['quantity']}{unit} (expires {e['expires_at']})")
        elif choice == "4":
            break
        else:
            print("Invalid choice.")

def main():
    init_db()
    while True:
        print("=== Family Grocery List ===")
        print("1. Show list")
        print("2. Add item")
        print("3. Toggle purchased")
        print("4. Remove item")
        print("5. Add recipe from URL (Spoonacular)")
        print("6. Add recipe by pasting ingredients")
        print("7. Quit")
        print("8. Pantry Menu")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            show_list()
        elif choice == "2":
            add_item()
        elif choice == "3":
            toggle_purchased()
        elif choice == "4":
            remove_item()
        elif choice == "5":
            add_recipe_from_url()
        elif choice == "6":
            add_recipe_by_paste()
        elif choice == "7":
            print("Goodbye!")
            break
        elif choice == "8":
            pantry_menu()
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()

