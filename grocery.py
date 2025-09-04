import os

FILE_PATH = "data/grocery_list.txt"

def parse_line(line: str):
    """Convert a saved line into a dict: {'name': str, 'purchased': bool}"""
    line = line.rstrip("\n")
    if line.startswith("[x] "):
        return {"name": line[4:], "purchased": True}
    if line.startswith("[ ] "):
        return {"name": line[4:], "purchased": False}
    # Backward compatibility: plain lines are treated as not purchased
    return {"name": line, "purchased": False}

def format_line(item: dict):
    """Convert an item dict back to a saveable line."""
    box = "[x]" if item["purchased"] else "[ ]"
    return f"{box} {item['name']}"

def load_list():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r") as f:
        lines = f.read().splitlines()
    return [parse_line(line) for line in lines if line.strip()]

def save_list(items):
    with open(FILE_PATH, "w") as f:
        for item in items:
            f.write(format_line(item) + "\n")

def show_list(items):
    if not items:
        print("\nYour grocery list is empty.\n")
        return
    print("\nGrocery List:")
    for i, item in enumerate(items, 1):
        box = "☑" if item["purchased"] else "☐"
        print(f"{i}. {box} {item['name']}")
    print()

def add_item(items):
    name = input("Enter item to add: ").strip()
    if not name:
        print("No item entered.")
        return
    items.append({"name": name, "purchased": False})
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
