import sqlite3
from time import sleep

# Database connection
conn = sqlite3.connect('link_manager.db')
cur = conn.cursor()

# Create table if not exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS LINK(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        link TEXT NOT NULL,
        description TEXT      
    )
""")


def list_all():
    """List all saved links"""
    cur.execute("SELECT * FROM LINK")
    rows = cur.fetchall()

    if not rows:
        print("\nNo links found.\n")
        return

    print("\nAll Links:")
    print("-" * 30)
    for data in rows:
        print(f"ID: {data[0]}")
        print(f"Name: {data[1]}")
        print(f"Link: {data[2]}")
        print(f"Description: {data[3]}")
        print("-" * 30)


def add():
    """Add a new link"""
    name = input("Enter name of the video: ").strip()
    link = input("Enter link of the video: ").strip()
    description = input("Enter description of the video: ").strip()

    if not name or not link:
        print("Name and Link are required")
        return

    cur.execute(
        "INSERT INTO LINK (name, link, description) VALUES (?, ?, ?)",
        (name, link, description)
    )
    conn.commit()
    print("Link added successfully!")


def update():
    """Update an existing link"""
    print("-" * 10, "Update", "-" * 10)

    try:
        link_id = int(input("Enter Link id: "))
    except ValueError:
        print("Enter a valid numeric id")
        return

    cur.execute("SELECT * FROM LINK WHERE id = ?", (link_id,))
    row = cur.fetchone()

    if not row:
        print("No link found with that id")
        return

    print("\nCurrent Values:")
    print(f"Name: {row[1]}")
    print(f"Link: {row[2]}")
    print(f"Description: {row[3]}\n")

    name = input("Enter new name (leave blank to keep same): ").strip()
    link = input("Enter new link (leave blank to keep same): ").strip()
    description = input("Enter new description (leave blank to keep same): ").strip()

    # Keep old values if user leaves blank
    name = name if name else row[1]
    link = link if link else row[2]
    description = description if description else row[3]

    cur.execute(
        "UPDATE LINK SET name = ?, link = ?, description = ? WHERE id = ?",
        (name, link, description, link_id)
    )
    conn.commit()
    print("Record updated successfully!")


def delete():
    """Delete a link"""
    print("-" * 10, "Delete", "-" * 10)

    try:
        link_id = int(input("Enter link id: "))
    except ValueError:
        print("Invalid id")
        return

    cur.execute("SELECT * FROM LINK WHERE id = ?", (link_id,))
    row = cur.fetchone()

    if not row:
        print("No link found with that id")
        return

    confirm = input(f"Are you sure you want to delete '{row[1]}'? (y/n): ").lower()
    if confirm != "y":
        print("Deletion cancelled")
        return

    cur.execute("DELETE FROM LINK WHERE id = ?", (link_id,))
    conn.commit()
    print("Deleted successfully")


def search():
    """Search for a link by ID"""
    print("-" * 10, "Search", "-" * 10)

    try:
        link_id = int(input("Enter the id: "))
    except ValueError:
        print("⚠️ Invalid id, must be a positive integer")
        return

    if link_id <= 0:
        print("Invalid id, must be greater than zero")
        return

    cur.execute("SELECT * FROM LINK WHERE id = ?", (link_id,))
    data = cur.fetchone()

    if data:
        print(f"ID: {data[0]}")
        print(f"Name: {data[1]}")
        print(f"Link: {data[2]}")
        print(f"Description: {data[3]}")
    else:
        print("Not found in the database.")


def main():
    """Main menu loop"""
    print("\n\n" + "-" * 8 + " Link Manager " + "-" * 8 + "\n")

    while True:
        print("1. List Links")
        print("2. Add Link")
        print("3. Update Link")
        print("4. Delete Link")
        print("5. Search Link")
        print("0. Exit")

        try:
            user_choice = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid input, enter a number 0-5")
            continue

        if user_choice == 0:
            print("Exiting ...")
            sleep(3)
            break

        match user_choice:
            case 1:
                list_all()
            case 2:
                add()
            case 3:
                update()
            case 4:
                delete()
            case 5:
                search()
            case _:
                print("Invalid choice, please enter 0-5")

    conn.close()


if __name__ == "__main__":
    main()
