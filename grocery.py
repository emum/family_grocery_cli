import os
import datetime

# File to store grocery list
FILE_PATH = "data/grocery_list.txt"

def load_list():
    """Load grocery list from file"""
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r") as f:
        items = f.read().splitlines()
    return items

def save_list(items):
    """Save grocery list to file"""
    with open(FILE_PATH, "w") as f:
        for item in items:
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(item + " created_at: " + created_at + "\n")

def show_list(items):
    """Display grocery list"""
    if not items:
        print("\nYour grocery list is empty.\n")
    else:
        print("\nGrocery List:")
        for i, item in enumerate(items, 1):
            print(f"{i}. {item}")
        print()

def edit_list(items):
    """Display grocery list"""
    if not items:
        print("\nYour grocery list is empty.\n")
    else:
        print("\nGrocery List:")
        for i, item in enumerate(items, 1):
            print(f"{i}. {item}")
        print()

def main():
    items = load_list()

    while True:
        print("=== Family Grocery List ===")
        print("1. Show list")
        print("2. Add item")
        print("3. Remove item")
        print("4. Quit")
        
        choice = input("Choose an option: ")

        if choice == "1":
            show_list(sorted(items))
        elif choice == "2":
            item = input("Enter item to add: ")
            items.append(item)
            save_list(items)
        elif choice == "3":
            show_list(items)
            try:
                num = int(input("Enter number of item to remove: "))
                if 1 <= num <= len(items):
                    removed = items.pop(num - 1)
                    print(f"Removed: {removed}")
                    save_list(items)
                else:
                    print("Invalid number.")
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()
