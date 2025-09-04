import os
from datetime import datetime

FILE_PATH = "data/grocery_list.txt"

# Change to "time" if you prefer unpurchased first, then oldest -> newest
SORT_MODE = "name"  # "name" or "time"

TIME_FMT = "%Y-%m-%d %H:%M"  # stored and displayed format

def now_str():
    return datetime.now().strftime(TIME_FMT)

def parse_line(line: str):
    """
    Convert a saved line into a dict: {'name': str, 'purchased': bool, 'added_at': str}
    Supported formats:
      "[ ] Milk | 2025-09-04 14:32"
      "[x] Eggs | 2025-09-04 14:33"
      Legacy (no timestamp): "[ ] Bread" or "Bread"
    """
    line = line.rstrip("\n")
    purchased = False
    name_part = line

    if line.startswith("[x] "):
        purchased = True
        name_part = line[4:]
    elif line.startswith("[ ] "):
        purchased = False
        name_part = line[4:]

    if " | " in name_part:
        name, added_at = name_part.split(" | ", 1)
        added_at = added_at.strip()
    else:
        # Legacy item without timestamp: give it one on next save
        name = name_part.strip()
        added_at = now_str()

    return {"name": name, "purchased": purchased, "added_at": added_at}

def format_line(item: dict):
    """Convert an item dict back to a saveable line."""
    box = "[x]" if item["purchased"] else "[ ]"
    return f"{box} {item['name']} | {item['added_at']}"

def load_list():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    items = [parse_line(ln) for ln in lines]
    return autosort(items)

def save_list(items):
    items = autosort(items)
    with open(FILE_PATH, "w") as f:
        for item in items:
            f.write(format_line(item) + "\n")

def autosort(items):
    """
    Unpurchased first, then:
      - by name (case-insensitive) if SORT_MODE == "name"
      - by added_at (oldest first) if SORT_MODE == "time"
    """
    if SORT_MODE == "time":
        key_fn = lambda it: (
            it["purchased"],
            datetime.strptime(it["added_at"], TIME_FMT)
        )
    else:
        key_fn = lambda it: (it["purchased"], it["name"].lower())

    return sorted(items, key=key_fn)

def show_list(items):
    if not items:
        print("\nYour grocery list is empty.\n")
        return
    print("\nGrocery List (auto-sorted: unpurchased first; by " + SORT_MODE + "):")
    for i, item in enumerate(items, 1):
        box = "☑" if item["purchased"] else "☐"
        print(f"{i}. {box} {item['name']}  —  added {item['added_at']}")
    print()

def add_item(items):
    name = input("Enter item to add: ").strip()
    if not name:
        print("No item entered.")
        return
    items.append({"name": name, "purchased": False, "added_at": now_str()})
    save_list(items)
    print(f"Added: {name}")

def remove_item(items):
    if not items:
        print("Nothing to remove.")
        return
    show_list(items)
    try:
        num = int(input("Enter number of item to remove: "))
        if 1 <= num <= len(items):
            removed = items.pop(num - 1)
            save_list(items)
            print(f"Removed: {removed['name']}")
        else:
            print("Invalid number.")
    except ValueError:
        print("Please enter a valid number.")

def toggle_purchased(items):
    if not items:
        print("Nothing to toggle.")
        return
    show_list(items)
    try:
        num = int(input("Enter number of item to toggle purchased: "))
        if 1 <= num <= len(items):
            items[num - 1]["purchased"] = not items[num - 1]["purchased"]
            state = "purchased" if items[num - 1]["purchased"] else "not purchased"
            save_list(items)
            print(f"Marked '{items[num - 1]['name']}' as {state}.")
        else:
            print("Invalid number.")
    except ValueError:
        print("Please enter a valid number.")

def main():
    items = load_list()
    while True:
        print("=== Family Grocery List ===")
        print("1. Show list")
        print("2. Add item")
        print("3. Toggle purchased")
        print("4. Remove item")
        print("5. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            show_list(items)
        elif choice == "2":
            add_item(items)
        elif choice == "3":
            toggle_purchased(items)
        elif choice == "4":
            remove_item(items)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()
