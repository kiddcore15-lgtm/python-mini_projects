
import sqlite3
import pywhatkit
import time
from datetime import datetime, date

DB = sqlite3.connect("birthday.db")
DB.row_factory = sqlite3.Row

DB.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    birthday TEXT,
    sent_year INTEGER DEFAULT 0
)
""")
DB.commit()


def add_contact():
    name = input("Enter name: ")
    phone = input("Enter WhatsApp number (+919876543210): ")
    birthday = input("Enter birthday (DD-MM): ")

    datetime.strptime(birthday, "%d-%m")

    DB.execute("""
    INSERT INTO contacts(name, phone, birthday)
    VALUES (?, ?, ?)
    """, (name, phone, birthday))

    DB.commit()
    print("Contact added successfully!")


def view_contacts():
    try:
        contacts = DB.execute(
            "SELECT * FROM contacts ORDER BY id"
        ).fetchall()

        print("\n========== SAVED BIRTHDAY CONTACTS ==========")

        if not contacts:
            print("No contacts found!")
            return

        for c in contacts:
            print("--------------------------------")
            print("ID:", c["id"])
            print("Name:", c["name"])
            print("Number:", c["phone"])
            print("Birthday:", c["birthday"])

        print("--------------------------------")
        print("Total contacts:", len(contacts))

    except Exception as error:
        print("Unable to display contacts:", error)

def delete_contact():
    contact_id = int(input("Enter Contact ID: "))

    DB.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    DB.commit()

    print("Contact deleted!")


def send_birthday_wishes():

    today = date.today().strftime("%d-%m")
    year = date.today().year

    contacts = DB.execute("""
        SELECT * FROM contacts
        WHERE birthday = ? AND sent_year != ?
    """, (today, year)).fetchall()

    if not contacts:
        print("No birthdays today!")
        return

    for person in contacts:

        name = person["name"]
        phone = person["phone"]

        message = (
            f"Happy Birthday {name}! 🎂🎉\n"
            "Wishing you lots of happiness, "
            "success and good health! Have a wonderful day! 🎈"
        )

        print("\n================================")
        print("BIRTHDAY FOUND!")
        print("Person:", name)
        print("WhatsApp Number:", phone)
        print("Sending birthday wish...")
        print("================================")

        try:
            pywhatkit.sendwhatmsg_instantly(
                phone,
                message,
                wait_time=20,
                tab_close=True
            )

            DB.execute("""
                UPDATE contacts
                SET sent_year = ?
                WHERE id = ?
            """, (year, person["id"]))

            DB.commit()

            print("Birthday wish sent successfully!")

            time.sleep(10)

        except Exception as error:
            print("Sending failed:", error)


def automatic_scheduler():

    print("\nAutomatic Birthday Scheduler Started!")
    print("Checking birthdays daily at 9:00 AM.")
    print("Keep your computer and WhatsApp Web running.")

    while True:

        now = datetime.now()

        if now.hour == 9 and now.minute == 0:
            send_birthday_wishes()

            # Prevent repeated checks during the same minute.
            time.sleep(60)

        time.sleep(10)


def menu():

    while True:

        print("\n================================")
        print("   WHATSAPP BIRTHDAY SENDER")
        print("================================")
        print("1. Add Birthday Contact")
        print("2. View All Contacts")
        print("3. Delete Contact")
        print("4. Send Today's Birthday Wishes")
        print("5. Start Automatic Scheduler")
        print("0. Exit")
        print("================================")

        choice = input("Enter choice: ")

        try:
            if choice == "1":
                add_contact()

            elif choice == "2":
                view_contacts()

            elif choice == "3":
                delete_contact()

            elif choice == "4":
                send_birthday_wishes()

            elif choice == "5":
                automatic_scheduler()

            elif choice == "0":
                print("Thank you!")
                break

            else:
                print("Invalid choice!")

        except ValueError as error:
            print("Input error:", error)

        except Exception as error:
            print("Error:", error)


if __name__ == "__main__":
    menu()
    DB.close()
