from datetime import datetime, timedelta
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return str(self.id)

    @staticmethod
    def find_by_email(email):
        return User.query.filter_by(email=email).first()

    @classmethod
    def create(cls, email, is_admin=False):
        user = cls(email=email, is_admin=is_admin)
        db.session.add(user)
        db.session.commit()
        return user

class VerificationCode(db.Model):
    __tablename__ = 'verification_codes'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def create(email):
        from random import randint
        code = str(randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=15)

        verification = VerificationCode(
            email=email,
            code=code,
            expires_at=expires_at
        )
        db.session.add(verification)
        db.session.commit()
        return code

    @staticmethod
    def verify(email, code):
        verification = VerificationCode.query.filter_by(
            email=email,
            code=code
        ).filter(VerificationCode.expires_at > datetime.utcnow()).first()

        if verification:
            VerificationCode.query.filter_by(email=email).delete()
            db.session.commit()
            return True
        return False

class BlogCategory(db.Model):
    __tablename__ = 'blog_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    blogs = db.relationship('Blog', backref='category', lazy=True)

class Blog(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('blog_categories.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_all(status=None):
        query = Blog.query
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Blog.created_at.desc()).all()

    @staticmethod
    def get(blog_id):
        return Blog.query.get(blog_id)