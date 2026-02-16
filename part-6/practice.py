import os
from flask import Flask, render_template , request , redirect , url_for , flash
from flask_sqlalcemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY' , 'fallback-secret-key')

DATABASE_URL = os.getenv('DATABASE_URL' , 'sqlite:///default.db')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return{
            'id' : self.id,
            'name' : self.name,
            'quantity' : self.quantity,
            'price' : self.price
        }

@app.route('/' , methods = ['GET'])
def index():
    products = Product.query.all()
    return jsonify({
        'success' : True,
        'count' : len(products),
        'products' : [product.to_dict() for product in products]

    })


