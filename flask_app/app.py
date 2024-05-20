from flask import Flask, jsonify, request, render_template_string, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the first entity (model)
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

# Define the second entity (model)
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    publication_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    author = db.relationship('Author', backref=db.backref('books', lazy=True))

# Create all tables
with app.app_context():
    db.create_all()

# Controller for Author
@app.route('/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify([{'id': a.id, 'name': a.name} for a in authors])

# Controller for Book
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{'id': b.id, 'title': b.title, 'publication_date': b.publication_date, 'author_id': b.author_id, 'author_name': b.author.name} for b in books])

# HealthCheck controller
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

# Home page
@app.route('/')
def index_page():
    return render_template_string('''
        <html>
        <head><title>Home</title></head>
        <body>
            <h1>Library Home Page</h1>
            <h2>Add a New Author</h2>
            <form action="/authors" method="POST">
                <label for="name">Author Name:</label>
                <input type="text" id="name" name="name" required><br><br>
                <input type="submit" value="Add Author">
            </form>
            <h2>Add a New Book</h2>
            <form action="/books" method="POST">
                <label for="title">Book Title:</label>
                <input type="text" id="title" name="title" required><br><br>
                <label for="author">Author Name:</label>
                <input type="text" id="author" name="author" required><br><br>
                <input type="submit" value="Add Book">
            </form>
            <a href="/authors">View Authors</a><br>
            <a href="/books">View Books</a><br>
            <a href="/health">Health Check</a>
        </body>
        </html>
    ''')

# Create Author
@app.route('/authors', methods=['POST'])
def create_author():
    name = request.form['name']

    author = Author.query.filter_by(name=name).first()
    if author is None:
        author = Author(name=name)
        db.session.add(author)
        db.session.commit()

    return redirect('/')

# Create Book
@app.route('/books', methods=['POST'])
def create_book():
    title = request.form['title']
    author_name = request.form['author']

    author = Author.query.filter_by(name=author_name).first()
    if author is None:
        author = Author(name=author_name)
        db.session.add(author)
        db.session.commit()

    book = Book(title=title, author_id=author.id)
    db.session.add(book)
    db.session.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
