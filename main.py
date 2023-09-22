import sqlite3
import datetime

# Create and connect to the database
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS Books (
                    BookID INTEGER PRIMARY KEY,
                    Title TEXT,
                    Author TEXT,
                    ISBN TEXT,
                    Status TEXT
                 )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                    UserID INTEGER PRIMARY KEY,
                    Name TEXT,
                    Email TEXT
                 )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Reservations (
                    ReservationID INTEGER PRIMARY KEY,
                    BookID INTEGER,
                    UserID INTEGER,
                    ReservationDate TEXT,
                    FOREIGN KEY (BookID) REFERENCES Books (BookID),
                    FOREIGN KEY (UserID) REFERENCES Users (UserID)
                 )''')


def add_book():
    title = input("Enter the book title: ")
    author = input("Enter the author: ")
    isbn = input("Enter the ISBN: ")
    status = "Available"
    cursor.execute("INSERT INTO Books (Title, Author, ISBN, Status) VALUES (?, ?, ?, ?)", (title, author, isbn, status))
    conn.commit()
    print("Book added successfully!")


def find_book_details():
    book_id = input("Enter the BookID: ")
    cursor.execute('''SELECT Books.Title, Books.Author, Books.Status, Users.Name, Users.Email
                      FROM Books
                      LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                      LEFT JOIN Users ON Reservations.UserID = Users.UserID
                      WHERE Books.BookID = ?''', (book_id,))
    result = cursor.fetchone()
    if result:
        title, author, status, user_name, user_email = result
        if user_name:
            print(f"Title: {title}")
            print(f"Author: {author}")
            print(f"Status: {status}")
            print(f"Reserved by: {user_name} ({user_email})")
        else:
            print(f"Title: {title}")
            print(f"Author: {author}")
            print(f"Status: {status}")
            print("Not reserved by any user.")
    else:
        print("Book not found!")


def find_reservation_status():
    text = input("Enter BookID, Title, UserID, or ReservationID: ")
    if text.startswith("LB"):
        cursor.execute('''SELECT Books.Status, Users.Name, Users.Email, Reservations.ReservationDate
                          FROM Books
                          LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                          LEFT JOIN Users ON Reservations.UserID = Users.UserID
                          WHERE Books.BookID = ?''', (text,))
    elif text.startswith("LU"):
        cursor.execute('''SELECT Books.Title, Books.Status, Reservations.ReservationDate
                          FROM Books
                          LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                          WHERE Reservations.UserID = ?''', (text,))
    elif text.startswith("LR"):
        cursor.execute('''SELECT Books.Title, Users.Name, Users.Email, Reservations.ReservationDate
                          FROM Reservations
                          LEFT JOIN Books ON Reservations.BookID = Books.BookID
                          LEFT JOIN Users ON Reservations.UserID = Users.UserID
                          WHERE Reservations.ReservationID = ?''', (text,))
    else:
        cursor.execute('''SELECT Books.BookID, Books.Title, Books.Author, Books.Status,
                          Users.UserID, Users.Name, Users.Email, Reservations.ReservationID, Reservations.ReservationDate
                          FROM Books
                          LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                          LEFT JOIN Users ON Reservations.UserID = Users.UserID
                          WHERE Books.Title = ?''', (text,))

    results = cursor.fetchall()
    if results:
        for result in results:
            print(result)
    else:
        print("No matching records found!")


def find_all_books():
    cursor.execute('''SELECT Books.BookID, Books.Title, Books.Author, Books.Status,
                      Users.UserID, Users.Name, Users.Email, Reservations.ReservationID, Reservations.ReservationDate
                      FROM Books
                      LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                      LEFT JOIN Users ON Reservations.UserID = Users.UserID''')

    results = cursor.fetchall()
    if results:
        for result in results:
            print(result)
    else:
        print("No books found!")


def reserve_book():
    book_id = input("Enter the BookID to reserve: ")
    user_id = input("Enter the UserID of the reserver: ")
    reservation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO Reservations (BookID, UserID, ReservationDate) VALUES (?, ?, ?)",
                   (book_id, user_id, reservation_date))
    cursor.execute("UPDATE Books SET Status = 'Reserved' WHERE BookID = ?", (book_id,))
    conn.commit()
    print("Book reserved successfully!")


def return_book():
    book_id = input("Enter the BookID to return: ")
    cursor.execute("DELETE FROM Reservations WHERE BookID = ?", (book_id,))
    cursor.execute("UPDATE Books SET Status = 'Available' WHERE BookID = ?", (book_id,))
    conn.commit()
    print("Book returned successfully!")


def update_book_details():
    book_id = input("Enter the BookID to update: ")
    new_status = input("Enter the new status: ")

    # Check if the update involves reservation status
    if new_status.lower() == "reserved":
        cursor.execute("UPDATE Books SET Status = 'Reserved' WHERE BookID = ?", (book_id,))
        conn.commit()

        # Check if the book is already reserved
        cursor.execute("SELECT * FROM Reservations WHERE BookID = ?", (book_id,))
        reservation = cursor.fetchone()
        if reservation is None:
            print("Book status updated to 'Reserved', but there are no reservations yet.")
        else:
            print("Book status updated to 'Reserved', and existing reservations remain.")
    else:
        cursor.execute("UPDATE Books SET Status = ? WHERE BookID = ?", (new_status, book_id))
        conn.commit()
        print("Book details updated!")


def delete_book():
    book_id = input("Enter the BookID to delete: ")

    # Check if the book is reserved
    cursor.execute("SELECT * FROM Reservations WHERE BookID = ?", (book_id,))
    reservation = cursor.fetchone()

    if reservation is not None:
        # Book is reserved, delete from both Books and Reservations tables
        cursor.execute("DELETE FROM Books WHERE BookID = ?", (book_id,))
        cursor.execute("DELETE FROM Reservations WHERE BookID = ?", (book_id,))
        conn.commit()
        print("Book and reservation deleted successfully!")
    else:
        # Book is not reserved, delete only from the Books table
        cursor.execute("DELETE FROM Books WHERE BookID = ?", (book_id,))
        conn.commit()
        print("Book deleted!")


# Add these functions to your existing code within the while loop where you handle user choices.

while True:
    print("\nLibrary Management System Menu:")
    print("1. Add a new book")
    print("2. Find a book's detail by BookID")
    print("3. Find reservation status by BookID, Title, UserID, or ReservationID")
    print("4. Find all books")
    print("5. Update book details by BookID")
    print("6. Delete a book by BookID")
    print("7. Reserve a book")
    print("8. Return a book")
    print("9. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_book()
    elif choice == "2":
        find_book_details()
    elif choice == "3":
        find_reservation_status()
    elif choice == "4":
        find_all_books()
    elif choice == "5":
        update_book_details()
    elif choice == "6":
        delete_book()
    elif choice == "7":
        reserve_book()
    elif choice == "8":
        return_book()
    elif choice == "9":
        print("Exiting...")
        break
    else:
        print("Invalid choice. Please try again.")

# Close the database connection
conn.close()
