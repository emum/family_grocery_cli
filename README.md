🛒 Family Grocery List CLI

A simple command-line app to help a family of four manage their grocery list.
This is the Level 1 prototype in a bigger 3-month Python learning journey.

📖 Features

Add grocery items

Remove grocery items

View full grocery list

Data is saved between runs (stored in data/grocery_list.txt)

▶️ How to Run

Clone/download this project folder.

Make sure you have Python 3.11+ installed.

Open a terminal in the project folder and run:

python grocery.py


Follow the on-screen menu:

=== Family Grocery List ===
1. Show list
2. Add item
3. Remove item
4. Quit

📂 Project Structure
family_grocery_cli/
│── grocery.py             # main Python script
│── data/
│    └── grocery_list.txt  # saved list (auto-created if missing)
│── README.md              # documentation & progress tracker

✅ Example Usage
=== Family Grocery List ===
1. Show list
2. Add item
3. Remove item
4. Quit
Choose an option: 2
Enter item to add: Milk


Result in data/grocery_list.txt:

Milk

🚀 Learning Roadmap (3 Months)

This project will grow step by step. Check things off ✅ as you go!

Month 1 – Python Foundations

 Create project folder + scaffold files

 Build grocery list CLI (add, remove, view)

 Save/load list from file (persistence)

 Add “mark as purchased” feature

 Auto-sort list alphabetically

 Add timestamps when items are added

Month 2 – Databases + APIs

 Replace text file with SQLite database

 Support multiple lists (Groceries, Chores, To-Do)

 Connect to recipe API → auto-generate grocery items

 Track pantry items with expiration dates

Month 3 – Notifications + Web App

 Send weekly grocery list via email

 Add SMS reminders for key items

 Build Flask web app for family dashboard

 Add user logins for family members

 Show charts of weekly food spending

 Suggest meals based on pantry + budget

👤 Author

Eric Mums — Python learner, building this as part of a 3-month project-based journey.