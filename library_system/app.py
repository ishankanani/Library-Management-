from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    publication_date = db.Column(db.String(255), nullable=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Initialize database
with app.app_context():
    db.create_all()

# Dummy database of users for Basic Auth (could be replaced with real data)
users = {"admin": "password123", "user": "mypassword"}

# Basic Authentication helper
def check_auth(username, password):
    return users.get(username) == password

def authenticate():
    return jsonify({"message": "Authentication required"}), 401

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Register user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

# Login user
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Check if the expected keys are present in the request data
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400

    username = data['username']
    password = data['password']
    
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        return jsonify({"message": "Logged in successfully!"})

    return jsonify({"message": "Invalid credentials"}), 401

# Add a book (with Basic Auth)
@app.route('/books', methods=['POST'])
@requires_auth
def add_book():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    title = data.get('title')
    author = data.get('author')
    isbn = data.get('isbn')

    if not title or not isinstance(title, str):
        return jsonify({"message": "Title must be a string"}), 422
    if not author or not isinstance(author, str):
        return jsonify({"message": "Author must be a string"}), 422
    if not isbn or not isinstance(isbn, str):
        return jsonify({"message": "ISBN must be a string"}), 422

    publication_date = data.get('publication_date')
    if publication_date and not isinstance(publication_date, str):
        return jsonify({"message": "Publication date must be a string"}), 422

    if len(isbn) != 13:
        return jsonify({"message": "ISBN must be 13 characters long"}), 400

    existing_book = Book.query.filter_by(isbn=isbn).first()
    if existing_book:
        return jsonify({"message": "Book with this ISBN already exists"}), 400

    new_book = Book(
        title=title, 
        author=author, 
        isbn=isbn, 
        publication_date=publication_date
    )
    db.session.add(new_book)
    db.session.commit()

    return jsonify({"message": "Book added successfully"}), 201

# Get all books (with Basic Auth)
@app.route('/books', methods=['GET'])
@requires_auth
def get_books():
    search = request.args.get('search', '')
    books = Book.query.filter(
        (Book.title.ilike(f"%{search}%")) | (Book.author.ilike(f"%{search}%"))
    ).all()

    books_list = [{"id": book.id, "title": book.title, "author": book.author, 
                   "publication_date": book.publication_date, "isbn": book.isbn} for book in books]

    return jsonify({
        "books": books_list
    })

# Update book (with Basic Auth)
@app.route('/books/<int:book_id>', methods=['PUT'])
@requires_auth
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()

    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.publication_date = data.get('publication_date', book.publication_date)
    book.isbn = data.get('isbn', book.isbn)

    db.session.commit()
    return jsonify({"message": "Book updated successfully"}), 200

# Delete book (with Basic Auth)
@app.route('/books/<int:book_id>', methods=['DELETE'])
@requires_auth
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"}), 200

# Add a member (with Basic Auth)
@app.route('/members', methods=['POST'])
@requires_auth
def add_member():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"message": "Name and email are required"}), 400

    if Member.query.filter_by(email=email).first():
        return jsonify({"message": "Member with this email already exists"}), 400

    new_member = Member(name=name, email=email)
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "Member added successfully"}), 201

@app.route('/members', methods=['GET'])
@requires_auth
def get_members():
    members = Member.query.all()

    members_list = [{"id": member.id, "name": member.name, "email": member.email} for member in members]

    return jsonify({
        "members": members_list
    })

# Get books by search query using id and author (with Basic Auth)
@app.route('/books', methods=['GET'])
@requires_auth
def search_books():
    book_id = request.args.get('id', None)  # Get 'id' parameter
    author = request.args.get('author', '')  # Get 'author' parameter

    # Debugging: Print out the parameters to check if they are correctly received
    print(f"Search Parameters - ID: {book_id}, Author: {author}")

    # If both id and author are provided
    if book_id and author:
        book = Book.query.filter_by(id=book_id, author=author).first()
        if book:
            books_list = [{"id": book.id, "title": book.title, "author": book.author, 
                           "publication_date": book.publication_date, "isbn": book.isbn}]
        else:
            return jsonify({"message": "No book found with the given ID and author"}), 404

    # If only id is provided
    elif book_id:
        book = Book.query.get(book_id)
        if book:
            books_list = [{"id": book.id, "title": book.title, "author": book.author, 
                           "publication_date": book.publication_date, "isbn": book.isbn}]
        else:
            return jsonify({"message": "Book not found with the given ID"}), 404

    # If only author is provided
    elif author:
        books = Book.query.filter(Book.author.ilike(f"%{author}%")).all()
        if books:
            books_list = [{"id": book.id, "title": book.title, "author": book.author, 
                           "publication_date": book.publication_date, "isbn": book.isbn} for book in books]
        else:
            return jsonify({"message": "No books found for the given author"}), 404

    else:
        return jsonify({"message": "Please provide either an id or an author to search"}), 400

    return jsonify({"books": books_list})

if __name__ == '__main__':
    app.run(debug=True)