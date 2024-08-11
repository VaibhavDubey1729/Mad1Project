from application.database import db

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(200), nullable=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    niche = db.Column(db.String(100), nullable=True)
    followers=db.Column(db.Integer, default=0)
    following=db.Column(db.Integer, default=0)
    visibility=db.Column(db.String, default='Private')
    flag=db.Column(db.Boolean, default=False)
    flagCount=db.Column(db.Integer, default=0)
    products = db.relationship('UserProduct', backref='user')


class Sponsor(db.Model):
    __tablename__ = 'Sponsor'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(200), unique=True, nullable=False)
    username = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    products = db.relationship('Product', backref='Sponsor', lazy=True)
    flag=db.Column(db.Boolean, default=False)
    flagCount=db.Column(db.Integer, default=0)

class Product(db.Model):
    __tablename__ = 'Product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    niche = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Integer, nullable=False)
    start = db.Column(db.Date, nullable=False)
    end = db.Column(db.Date, nullable=False)
    Ads=db.Column(db.Integer,nullable=True)
    CompletedAd=db.Column(db.Integer,nullable=True)
    visibility=db.Column(db.String, default='Private')
    flag=db.Column(db.Boolean, default=False)
    flagCount=db.Column(db.Integer, default=0)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('Sponsor.id'), nullable=False)
    users = db.relationship('User', secondary='userproduct', backref='product')

class UserProduct(db.Model):
    __tablename__ = 'userproduct'
    productID = db.Column(db.Integer, db.ForeignKey('Product.id'), primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    progress=db.Column(db.Integer,nullable=True, default=0)
    status = db.Column(db.String(20), default='Pending')  # Status: Pending, Accepted, Rejected, Waiting, Completed
    budget=db.Column(db.Integer, nullable=True)
    flag=db.Column(db.Boolean, default=False)
    negotiation=db.Column(db.String, nullable=True)
    