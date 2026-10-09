"""
Campus Resource Management System - Learn2Earn
Python standard library only.
"""

import json
import os

# ----------------------------------------------------------
# STARTING DATA
# ----------------------------------------------------------
DATA_FILE = "campus_data.json"
LOW_STOCK_LIMIT = 3

resources = [
    {"id": "R001", "name": "Laptop", "category": "Electronics", "total": 10, "available": 10},
    {"id": "R002", "name": "Keyboard", "category": "Accessories", "total": 5, "available": 5},
    {"id": "R003", "name": "Headset", "category": "Accessories", "total": 3, "available": 3},
]
fellows = {"F001": "Ada", "F002": "John", "F003": "Grace"}
# Each record: {"fellow_id", "resource_id", "quantity", "type"}  (type = "borrow" or "return")
borrow_records = []


# ----------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------
def find_resource(resource_id):
    """Return the resource dict with this ID, or None."""
    for r in resources:
        if r["id"] == resource_id:
            return r
    return None


def is_positive_int(value):
    """True only for real integers greater than 0 (bool is not accepted)."""
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def parse_int(text):
    """Convert typed text to int (negatives allowed). Return None if not a whole number."""
    try:
        return int(text.strip())
    except (ValueError, AttributeError):
        return None


def units_on_loan(fellow_id, resource_id):
    """Units of a resource this fellow currently holds (borrows minus returns)."""
    total = 0
    for rec in borrow_records:
        if rec["fellow_id"] == fellow_id and rec["resource_id"] == resource_id:
            if rec["type"] == "borrow":
                total += rec["quantity"]
            else:
                total -= rec["quantity"]
    return total


# ----------------------------------------------------------
# INVENTORY
# ----------------------------------------------------------
def add_resource(resource_id, name, category, total):
    """Add a new resource. Returns True on success, False if rejected."""
    resource_id, name, category = resource_id.strip(), name.strip(), category.strip()
    if not resource_id or not name or not category:
        print("Error: ID, name and category cannot be empty.")
        return False
    if find_resource(resource_id) is not None:
        print(f"Error: a resource with ID '{resource_id}' already exists.")
        return False
    if not is_positive_int(total):
        print("Error: total units must be a positive whole number.")
        return False
    resources.append({"id": resource_id, "name": name, "category": category,
                      "total": total, "available": total})
    print(f"Added {name} ({resource_id}) with {total} units.")
    return True


def print_resources(items):
    """Print a list of resources as a table."""
    if not items:
        print("No resources found.")
        return
    print(f"{'ID':<8}{'Name':<15}{'Category':<15}{'Available/Total'}")
    print("-" * 52)
    for r in items:
        print(f"{r['id']:<8}{r['name']:<15}{r['category']:<15}{r['available']}/{r['total']}")


def list_resources():
    print_resources(resources)


# ----------------------------------------------------------
# BORROWING
# ----------------------------------------------------------
def borrow(fellow_id, resource_id, qty):
    """Validate everything first; only change data if all checks pass."""
    if fellow_id not in fellows:
        print(f"Error: unknown fellow ID '{fellow_id}'.")
        return False
    resource = find_resource(resource_id)
    if resource is None:
        print(f"Error: unknown resource ID '{resource_id}'.")
        return False
    if not is_positive_int(qty):
        print("Error: quantity must be a positive whole number.")
        return False
    if qty > resource["available"]:
        print(f"Error: only {resource['available']} {resource['name']}(s) available, "
              f"cannot lend {qty}.")
        return False

    resource["available"] -= qty
    borrow_records.append({"fellow_id": fellow_id, "resource_id": resource_id,
                           "quantity": qty, "type": "borrow"})
    print(f"{fellows[fellow_id]} borrowed {qty} {resource['name']}(s). "
          f"Available now: {resource['available']}")
    return True


# ----------------------------------------------------------
# RETURNS
# ----------------------------------------------------------
def return_item(fellow_id, resource_id, qty):
    """Only allow returning units the fellow currently has on loan."""
    if fellow_id not in fellows:
        print(f"Error: unknown fellow ID '{fellow_id}'.")
        return False
    resource = find_resource(resource_id)
    if resource is None:
        print(f"Error: unknown resource ID '{resource_id}'.")
        return False
    if not is_positive_int(qty):
        print("Error: quantity must be a positive whole number.")
        return False
    held = units_on_loan(fellow_id, resource_id)
    if qty > held:
        print(f"Error: {fellows[fellow_id]} only has {held} {resource['name']}(s) "
              f"on loan, cannot return {qty}.")
        return False

    resource["available"] += qty
    borrow_records.append({"fellow_id": fellow_id, "resource_id": resource_id,
                           "quantity": qty, "type": "return"})
    print(f"{fellows[fellow_id]} returned {qty} {resource['name']}(s). "
          f"Available now: {resource['available']}")
    return True


# ----------------------------------------------------------
# SEARCH AND FILTER
# ----------------------------------------------------------
def search_by_name(term):
    term = term.strip().lower()
    return [r for r in resources if term in r["name"].lower()]


def filter_by_category(category):
    category = category.strip().lower()
    return [r for r in resources if r["category"].lower() == category]


# ----------------------------------------------------------
# REPORTS
# ----------------------------------------------------------
def generate_report():
    total_units = sum(r["total"] for r in resources)
    available_units = sum(r["available"] for r in resources)
    borrowed_units = total_units - available_units

    low_stock = [r for r in resources if r["available"] < LOW_STOCK_LIMIT]

    leaders = []
    max_borrowed = 0
    if resources:
        max_borrowed = max(r["total"] - r["available"] for r in resources)
        if max_borrowed > 0:
            leaders = [r for r in resources if r["total"] - r["available"] == max_borrowed]

    print("========== INVENTORY REPORT ==========")
    print(f"Total units:      {total_units}")
    print(f"Available units:  {available_units}")
    print(f"Borrowed units:   {borrowed_units}")
    print(f"Low stock (fewer than {LOW_STOCK_LIMIT} available):")
    if low_stock:
        for r in low_stock:
            print(f"  - {r['name']} ({r['available']})")
    else:
        print("  None")
    if leaders:
        names = ", ".join(r["name"] for r in leaders)
        label = "Most borrowed" if len(leaders) == 1 else "Most borrowed (tie)"
        print(f"{label}: {names} ({max_borrowed})")
    else:
        print("Most borrowed: none, no units are currently borrowed")
    print("======================================")


# ----------------------------------------------------------
# BONUS: JSON SAVE AND LOAD
# ----------------------------------------------------------
def save_data(filename=DATA_FILE):
    try:
        with open(filename, "w") as f:
            json.dump({"resources": resources, "borrow_records": borrow_records}, f, indent=2)
        print(f"Data saved to {filename}.")
    except OSError as e:
        print(f"Could not save data: {e}")


def load_data(filename=DATA_FILE):
    if not os.path.exists(filename):
        return
    try:
        with open(filename) as f:
            data = json.load(f)
        resources[:] = data["resources"]
        borrow_records[:] = data["borrow_records"]
        print(f"Loaded saved data from {filename}.")
    except (OSError, ValueError, KeyError):
        print("Saved data file is unreadable; using starting data.")


# ----------------------------------------------------------
# DEMONSTRATION
# ----------------------------------------------------------
def run_demo():
    """Runs the 7 required steps plus one invalid-input test.
    Use on fresh starting data (delete campus_data.json first) for matching output."""
    print("\nSTEP 1: F001 borrows 2 laptops")
    borrow("F001", "R001", 2)
    print("\nSTEP 2: F002 borrows 3 keyboards")
    borrow("F002", "R002", 3)
    print("\nSTEP 3: F001 returns 1 laptop")
    return_item("F001", "R001", 1)
    print("\nSTEP 4: F003 requests 4 headsets (should be rejected)")
    borrow("F003", "R003", 4)
    print("\nSTEP 5: F002 tries to return 4 keyboards (should be rejected)")
    return_item("F002", "R002", 4)
    print("\nSTEP 6: Search for 'LAPtop'")
    print_resources(search_by_name("LAPtop"))
    print("\nSTEP 7: Report")
    generate_report()
    print("\nEXTRA TEST: F001 borrows -5 laptops (invalid input)")
    borrow("F001", "R001", -5)


# ----------------------------------------------------------
# MENU AND MAIN LOOP
# ----------------------------------------------------------
def print_menu():
    print("\n===== CAMPUS RESOURCE MANAGER =====")
    print("1. Add resource")
    print("2. List resources")
    print("3. Borrow")
    print("4. Return")
    print("5. Search by name")
    print("6. Filter by category")
    print("7. Report")
    print("8. Run demonstration")
    print("0. Exit")


def main():
    load_data()
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            rid = input("Resource ID: ")
            name = input("Name: ")
            category = input("Category: ")
            total = parse_int(input("Total units: "))
            add_resource(rid, name, category, total)
        elif choice == "2":
            list_resources()
        elif choice == "3":
            fid = input("Fellow ID: ").strip().upper()
            rid = input("Resource ID: ").strip().upper()
            qty = parse_int(input("Quantity: "))
            borrow(fid, rid, qty)
        elif choice == "4":
            fid = input("Fellow ID: ").strip().upper()
            rid = input("Resource ID: ").strip().upper()
            qty = parse_int(input("Quantity: "))
            return_item(fid, rid, qty)
        elif choice == "5":
            print_resources(search_by_name(input("Search name: ")))
        elif choice == "6":
            print_resources(filter_by_category(input("Category: ")))
        elif choice == "7":
            generate_report()
        elif choice == "8":
            run_demo()
        elif choice == "0":
            save_data()
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please enter a number from the menu.")


if __name__ == "__main__":
    main()