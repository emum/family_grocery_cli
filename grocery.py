from datetime import datetime
from db import init_db, list_items as db_list_items, add_item as db_add_item, remove_item as db_remove_item, toggle_purchased as db_toggle_purchased

SORT_MODE = "name"  # keep for display text, sorting is handled in SQL

def show_list():
    items = db_list_items()
    if not items:
        print("\nYour grocery list is empty.\n")
        return items
    print("\nGrocery List (auto-sorted: unpurchased first; by " + SORT_MODE + "):")
    for i, item in enumerate(items, 1):
        box = "☑" if item["purchased"] else "☐"
        print(f"{i}. {box} {item['name']}  —  added {item['added_at']}")
    print()
    return items

def add_item():
    name = input("Enter item to add: ").strip()
    if not name:
        print("No item entered.")
        return
    db_add_item(name)
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

def main():
    init_db()  # ensures table exists
    while True:
        print("=== Family Grocery List ===")
        print("1. Show list")
        print("2. Add item")
        print("3. Toggle purchased")
        print("4. Remove item")
        print("5. Quit")
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
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()
