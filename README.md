# Library Management System API

This is a simple Flask-based API for a Library Management System. It allows the following functionalities:

- Books : Create, Read, Update, Delete books.
- Members : Create and list members.
- Search Books : Search books by title or author.
- Pagination : Pagination for listing books.
- Token-based Authentication : Secure the endpoints using JWT tokens.

# Requirements
- Flask
- sqlite3 (standard Python library)

# How to run the project:
1. Clone the repository.
2. Install Flask
3. Run the application:
4. Access the API at `http://127.0.0.1:5000`.

# Design Choices:
- Token-based Authentication : Secure the API using JWT tokens.
- SQLite : Used `sqlite3` for database connectivity, no third-party libraries.
- Pagination : Implemented pagination for book listing to avoid large data retrieval at once.

# Assumptions and Limitations:
- Dummy authentication (username: admin, password: password).
- No real-world user validation or encryption.
- Minimal error handling for edge cases.
