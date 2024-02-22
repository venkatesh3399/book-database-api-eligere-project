from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Function to create the 'books' table in the SQLite database
def create_books_table():

    # Establish a connection to the SQLite database
    conn = sqlite3.connect('database/books.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            ISBN TEXT NOT NULL,
            publication_date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Call the function to create the 'books' table
create_books_table()

@app.route('/')
def index():
    return 'Welcome to Book API!'

# Function to add data into the table
@app.route('/books', methods=['POST'])
def create_book():

    data = request.json

    #Check if data is provided
    if not data:
        return jsonify({"error": "No data provided"}), 400

    #Define required fields
    required_fields = ['title', 'author', 'ISBN', 'publication_date']

    #Check if all required fields are present
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    #Check data types of fields
    if  not isinstance(data['title'], str) or \
        not isinstance(data['author'], str) or \
        not isinstance(data['ISBN'], str) or \
        not isinstance(data['publication_date'], str):
            return jsonify({'error' : "Incorrect data types"}), 400

    # Insert the new book entry into the database
    conn = sqlite3.connect('database/books.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO books (title, author, ISBN, publication_date)
        VALUES (?, ?, ?, ?)
    """, (data['title'], data['author'], data['ISBN'], data['publication_date']))
    conn.commit()

    # Return the ID of the newly created book entry
    book_id = cursor.lastrowid

    #Close cursor and connection
    cursor.close()
    conn.close()

    return jsonify({"id": book_id}), 201
 
# Function to get all available books from table
@app.route('/books', methods=['GET'])
def get_all_books():
    conn = sqlite3.connect('database/books.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    cursor.close()
    conn.close()

    book_list = []
    for book in books:
        book_dict = {
            "id": book[0],
            "title": book[1],
            "author": book[2],
            "ISBN": book[3],
            "publication_date": book[4]
        }
        book_list.append(book_dict)

    return jsonify(book_list), 200

# Function to get a particular book from table
@app.route('/books/<int:id>', methods=['GET'])
def get_book_by_id(id):
    conn = sqlite3.connect('database/books.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books WHERE id = ?", (id,))
    book = cursor.fetchone()

    cursor.close()
    conn.close()

    if book:
        book_dict = {
            "id": book[0],
            "title": book[1],
            "author": book[2],
            "ISBN": book[3],
            "publication_date": book[4]
        }
        return jsonify(book_dict), 200
    else:
        return jsonify({"error": "Book not found"}), 404

# Function to update a book from table
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    conn = sqlite3.connect('database/books.db')
    cursor = conn.cursor()

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Check if book with given ID exists
    cursor.execute("SELECT * FROM books WHERE id = ?", (id,))
    book = cursor.fetchone()
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Update the book entry in the database
    cursor.execute("""
        UPDATE books
        SET title = ?, author = ?, ISBN = ?, publication_date = ?
        WHERE id = ?
    """, (data.get('title', book[1]), data.get('author', book[2]), 
          data.get('ISBN', book[3]), data.get('publication_date', book[4]), id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Book updated successfully"}), 200

# Function to delete a book from table
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    conn = sqlite3.connect('database/books.db')
    cursor = conn.cursor()

    # Check if book with given ID exists
    cursor.execute("SELECT * FROM books WHERE id = ?", (id,))
    book = cursor.fetchone()
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Delete the book entry from the database
    cursor.execute("DELETE FROM books WHERE id = ?", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Book deleted successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True)
