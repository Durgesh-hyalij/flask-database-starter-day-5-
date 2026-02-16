from flask import Flask, request, jsonify , render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from sqlalchemy import or_
import jwt
from datetime import timedelta
from functools import wraps
import os

app = Flask(__name__)
# DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///api_demo.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_demo.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key'
    
db = SQLAlchemy(app)
CORS(app)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)
    # making relationship
    #one author can have many Books
    books = db.relationship("Book", backref='author' , lazy = True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bio': self.bio,
            'city': self.city
        }
    

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    
    year = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # foreign key
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable = False)


    # def to_dict(self):
    #     return {
    #         'id': self.id,
    #         'title': self.title,
    #         'year': self.year,
    #         'isbn': self.isbn,
    #         'created_at': self.created_at.isoformat() if self.created_at else None
    #     }

    def to_dict(self):
        return {
        'id': self.id,
        'title': self.title,
        'year': self.year,
        'isbn': self.isbn,
        'created_at': self.created_at.isoformat() if self.created_at else None,
        'author': {
            'id': self.author.id,
            'name': self.author.name,
            'city': self.author.city
        } if self.author else None
    }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # plain for now


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token missing'}), 401

        try:
            token = token.split()[1]
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return wrapper


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(
        username=data.get('username'),
        password=data.get('password')
    ).first()

    if not user:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'success': True,
        'token': token
    })




@app.route('/api/books', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 5, type=int)

    title = request.args.get('title')
    year = request.args.get('year')
    author = request.args.get('author')

    query = Book.query.join(Author)

    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))

    if year:
        query = query.filter(Book.year == year)

    if author:
        query = query.filter(Author.name.ilike(f"%{author}%"))

    pagination = query.order_by(Book.id.desc()).paginate(
        page=page,
        per_page=limit,
        error_out=False
    )

    #drh
    # 🔹 SORTING PARAMS
    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc")

    query = Book.query

    # 🔹 APPLY SORTING
    if sort_by == "title":
        query = query.order_by(Book.title.asc() if order == "asc" else Book.title.desc())

    elif sort_by == "year":
        query = query.order_by(Book.year.asc() if order == "asc" else Book.year.desc())

    elif sort_by == "id":
        query = query.order_by(Book.id.asc() if order == "asc" else Book.id.desc())

    #drh
    return jsonify({
        "success": True,
        "page": page,
        "total_pages": pagination.pages,
        "total_items": pagination.total,
        "books": [book.to_dict() for book in pagination.items]
    })


# GET /api/books - Get all books  (For Pagination i replace this)
# @app.route('/api/books', methods=['GET'])
# def get_books():
#     books = Book.query.all()
#     return jsonify({  # Return JSON response
#         'success': True,
#         'count': len(books),
#         'books': [book.to_dict() for book in books]  # List comprehension to convert all 
#     })

# IMP --> The "Long" way to write 'books': [book.to_dict() for book in books] 
# formatted_books = []
# for book in books:
#     formatted_books.append(book.to_dict())

# return {"books": formatted_books}

# GET /api/books/<id> - Get single book

@app.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({
            'success': False,
            'error': 'Book not found'
        }), 404  # Return 404 status code

    return jsonify({
        'success': True,
        'book': book.to_dict()
    })


# POST /api/books - Create new book
@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()  # Get JSON data from request body

    # Validation
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    if not data.get('title'):
        return jsonify({'success': False, 'error': 'Title  are required'}), 400

    # Check for duplicate ISBN
    if data.get('isbn'):
        existing = Book.query.filter_by(isbn=data['isbn']).first()
        if existing:
            return jsonify({'success': False, 'error': 'ISBN already exists'}), 400

    # Create book
    new_book = Book(
        title=data['title'],
        year=data.get('year'),  # Optional field
        isbn=data.get('isbn'),
        author_id=data.get('author_id')
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book created successfully',
        'book': new_book.to_dict()
    }), 201  # 201 = Created


# PUT /api/books/<id> - Update book
@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    # Update fields if provided
    if 'title' in data:
        book.title = data['title']
 
    if 'year' in data:
        book.year = data['year']
    if 'isbn' in data:
        book.isbn = data['isbn']
    
    if 'author_id' in data:
        book.author_id = data['author_id']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book updated successfully',
        'book': book.to_dict()
    })


# DELETE /api/books/<id> - Delete book
@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)

    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book deleted successfully'
    })




# =============================================================================
# BONUS: Search and Filter
# =============================================================================

# # GET /api/books/search?q=python&author=john
# @app.route('/api/books/search', methods=['GET'])
# def search_books():
#     query = Book.query

#     # Filter by title (partial match)
#     title = request.args.get('q')  # Query parameter: ?q=python
#     if title:
#         query = query.filter(Book.title.ilike(f'%{title}%'))  # Case-insensitive LIKE

#     # # Filter by author
#     # author = request.args.get('author')
#     # if author:
#     #     query = query.filter(Book.author.ilike(f'%{author}%'))

#     # Filter by year
#     year = request.args.get('year')
#     if year:
#         query = query.filter_by(year=int(year))

#     books = query.all()

#     return jsonify({
#         'success': True,
#         'count': len(books),
#         'books': [book.to_dict() for book in books]
#     })



@app.route('/api/books/search', methods=['GET'])
def search_books():
    query = Book.query

    # 🔍 Search by book title
    title = request.args.get('q')
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))

    # 📅 Filter by year
    year = request.args.get('year')
    if year:
        query = query.filter(Book.year == int(year))

    # 👤 Search by author name (JOIN)
    author_name = request.args.get('author')
    if author_name:
        query = query.join(Author).filter(
            Author.name.ilike(f'%{author_name}%')
        )

    books = query.all()

    return jsonify({
        'success': True,
        'count': len(books),
        'books': [book.to_dict() for book in books]
    })



# =============================================================================
# SIMPLE WEB PAGE FOR TESTING
# =============================================================================

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Part 4 - REST API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
            h1 { color: #e94560; }
            .endpoint { background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #e94560; }
            .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
            .get { background: #27ae60; }
            .post { background: #f39c12; }
            .put { background: #3498db; }
            .delete { background: #e74c3c; }
            code { background: #0f3460; padding: 2px 6px; border-radius: 3px; }
            pre { background: #0f3460; padding: 15px; border-radius: 8px; overflow-x: auto; }
            a { color: #e94560; }
        </style>
    </head>
    <body>
        <h1>Part 4: REST API Demo</h1>
        <p>This is a JSON API - use curl, Postman, or JavaScript fetch() to test!</p>

        <h2>API Endpoints:</h2>

        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/books</code> - Get all books
            <br><a href="/api/books" target="_blank">Try it →</a>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/books/&lt;id&gt;</code> - Get single book
        </div>

        <div class="endpoint">
            <span class="method post">POST</span>
            <code>/api/books</code> - Create new book
        </div>

        <div class="endpoint">
            <span class="method put">PUT</span>
            <code>/api/books/&lt;id&gt;</code> - Update book
        </div>

        <div class="endpoint">
            <span class="method delete">DELETE</span>
            <code>/api/books/&lt;id&gt;</code> - Delete book
        </div>

        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/books/search?q=&lt;title&gt;&author=&lt;name&gt;</code> - Search books
        </div>

        <h2>Test with curl:</h2>
        <pre>
# Get all books
curl http://localhost:5000/api/books

# Create a book
curl -X POST http://localhost:5000/api/books \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Flask Web Development", "author": "Miguel Grinberg", "year": 2018}'

# Update a book
curl -X PUT http://localhost:5000/api/books/1 \\
  -H "Content-Type: application/json" \\
  -d '{"year": 2023}'

# Delete a book
curl -X DELETE http://localhost:5000/api/books/1
        </pre>
    </body>
    </html>
    '''

# @app.route('/api/author', methods=['GET'])
# def get_authors():
#     authors = Author.query.all()
#     return jsonify({
#         'success': True,
#         'count': len(authors),
#         'authors': [author.to_dict() for author in authors]  # ✅ correct key
#     })
@app.route("/api/author" , methods = ['GET'])
def get_authors():
    page = request.args.get("page", 1, type=int)   # this two lines are for pagination
    limit = request.args.get("limit", 5, type=int)

    pagination = Author.query.paginate(page=page, per_page=limit, error_out=False)
    a = Author.query.all()
    authors = [author.to_dict() for author in pagination.items]

    return jsonify({
        "success": True,
        "authors": authors,
        "page": pagination.page,
        "total_pages": pagination.pages,
        "total_items": pagination.total
    })


@app.route('/api/authors/<int:id>' , methods = ['GET'])
def get_author(id):
    author = Author.query.get(id)

    if not author:
        return jsonify({
            'success' : True,
            'error' : 'Author not found'
        }), 404
    
    return jsonify({
        'success' : True,
        'author' : author.to_dict()
    })

@app.route('/api/authors' , methods=['POST'])
def create_authors():
    data = request.get_json()

    if not data:
        return jsonify({'success' : False,
                        'error' : "No data provided",                   
                        }), 400
    if not data.get('name') or not data.get('city') or not data.get("bio"):
        return jsonify({'succss' : False , 'error' : "NO name and city and bio provided"})
    
    new_author = Author(
        name = data.get('name'),
        bio  = data.get('bio'),
        city = data.get('city')
    )

    db.session.add(new_author)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'author created successfully',
        'author': new_author.to_dict()
    }), 201  # 201 = Created
    
    
# PUT /api/books/<id> - Update Author
@app.route('/api/authors/<int:id>', methods=['PUT'])
def author(id):
    author = Author.query.get(id)

    if not author:
        return jsonify({'success': False, 'error': 'author not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    # Update fields if provided
    if 'name' in data:
        author.name = data['name']
    if 'city' in data:
        author.city = data['city']
    if 'bio' in data:
        author.bio = data['bio']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book updated successfully',
        'author': author.to_dict()
    })


# DELETE /api/books/<id> - Delete book
@app.route('/api/authors/<int:id>', methods=['DELETE'])
def delete_author(id):
    author = Author.query.get(id)

    if not author:
        return jsonify({'success': False, 'error': 'author not found'}), 404

    db.session.delete(author)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'author deleted successfully'
    })



# def init_db():
#     with app.app_context():
#         db.create_all()

#         if Author.query.count() == 0:
#             sample_authors = [
#                 Author(name='Durgesh', city='Chandwad',  bio='978-1593279288'),
#                 Author(name='Harshal', city='Sambhaji nagar',  bio='978-1491991732'),
#                 Author(name='Gaurav', city='Nashik', bio='978-0132350884'),
#             ]
#             db.session.add_all(sample_authors)
#             db.session.commit()
#             print('Sample Author added!')

# def init_db():
#     with app.app_context():
#         db.create_all()

#         if Author.query.count() == 0:
#             a1 = Author(name='Durgesh', city='Chandwad', bio='Backend Developer')
#             a2 = Author(name='Harshal', city='Sambhajinagar', bio='Python Enthusiast')
#             a3 = Author(name='Gaurav', city='Nashik', bio='Software Engineer')

#             db.session.add_all([a1, a2, a3])
#             db.session.commit()

#         if Book.query.count() == 0:
#             b1 = Book(title='Python Crash Course', year=2019, isbn='111', author_id=1)
#             b2 = Book(title='Flask Web Development', year=2018, isbn='222', author_id=2)
#             b3 = Book(title='Clean Code', year=2008, isbn='333', author_id=3)

#             db.session.add_all([b1, b2, b3])
#             db.session.commit()

def init_db():
    with app.app_context():
        db.create_all()
        if Author.query.count() == 0:
            a1 = Author(name='Durgesh', city='Chandwad', bio='Backend Developer')
            a2 = Author(name='Harshal', city='Sambhajinagar', bio='Python Enthusiast')
            a3 = Author(name='Gaurav', city='Nashik', bio='Software Engineer')

            db.session.add_all([a1, a2, a3])
            db.session.commit()

        if Book.query.count() == 0:
            # Fetch authors safely
            durgesh = Author.query.filter_by(name='Durgesh').first()
            harshal = Author.query.filter_by(name='Harshal').first()
            gaurav = Author.query.filter_by(name='Gaurav').first()

            b1 = Book(title='Python Crash Course', year=2019, isbn='111', author_id=durgesh.id)
            b2 = Book(title='Flask Web Development', year=2018, isbn='222', author_id=harshal.id)
            b3 = Book(title='Clean Code', year=2008, isbn='333', author_id=gaurav.id)

            db.session.add_all([b1, b2, b3])
            db.session.commit()

        



if __name__ == '__main__':
    init_db()
    app.run(debug=True) 
    # app.run(debug=os.getenv('FLASK_DEBUG', 'True') == 'True')

