from datetime import datetime, timedelta
from random import randint
from flask_login import UserMixin
from bson import ObjectId
from pymongo import MongoClient
import os

# MongoDB connection
client = MongoClient(os.environ.get("MONGODB_URI", ""))
db = client.get_database(os.environ.get("MONGODB_DB", "portfolio"))

# Collections
users_col = db["users"]
verification_codes_col = db["verification_codes"]
blog_categories_col = db["blog_categories"]
blogs_col = db["blogs"]

# Indexes
users_col.create_index("email", unique=True)
verification_codes_col.create_index("email")
verification_codes_col.create_index("expires_at", expireAfterSeconds=0)  # TTL index
blogs_col.create_index("status")
blogs_col.create_index("category_id")

# ─────────────────────────────────────────────
# Seed: único usuário admin
# ─────────────────────────────────────────────
def seed_admin():
    existing = users_col.find_one({"_id": "@zeuss"})
    if not existing:
        users_col.insert_one({
            "_id": "@zeuss",
            "username": "Zeuss",
            "profile_picture": "https://lh3.googleusercontent.com/a/ACg8ocK3tgKjyw3ZAKz0aOBXFG4Twd1pvVHTRimFoeYHiC78RLvwypU=s288-c-no",
            "email": "zeuss.developer@gmail.com",
            "is_admin": True,
            "last_login": None,
            "created_at": datetime.utcnow()
        })
    
def seed_categories():
    if blog_categories_col.count_documents({}) == 0:
        blog_categories_col.insert_many([
            {"name": "Tecnologia", "description": "Posts sobre tecnologia e programação", "created_at": datetime.utcnow()},
            {"name": "Design", "description": "Posts sobre UI/UX e design gráfico", "created_at": datetime.utcnow()},
            {"name": "Projetos", "description": "Atualizações sobre meus projetos", "created_at": datetime.utcnow()},
        ])


# ─────────────────────────────────────────────
# User
# ─────────────────────────────────────────────
class User(UserMixin):
    def __init__(self, doc):
        self._id = doc["_id"]
        self.id = doc["_id"]          # Flask-Login usa get_id()
        self.email = doc["email"]
        self.username = doc.get("username", "")
        self.profile_picture = doc.get("profile_picture", "")
        self.is_admin = doc.get("is_admin", False)
        self.last_login = doc.get("last_login")
        self.created_at = doc.get("created_at")

    def get_id(self):
        return str(self._id)

    @staticmethod
    def find_by_email(email):
        doc = users_col.find_one({"email": email})
        return User(doc) if doc else None

    @staticmethod
    def find_by_id(user_id):
        doc = users_col.find_one({"_id": user_id})
        return User(doc) if doc else None

    @classmethod
    def create(cls, email, is_admin=False):
        doc = {
            "_id": "@zeuss",
            "username": "Zeuss",
            "profile_picture": "https://lh3.googleusercontent.com/a/ACg8ocK3tgKjyw3ZAKz0aOBXFG4Twd1pvVHTRimFoeYHiC78RLvwypU=s288-c-no",
            "email": email,
            "is_admin": is_admin,
            "last_login": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        users_col.insert_one(doc)
        return cls(doc)

    def update_last_login(self):
        users_col.update_one({"_id": self._id}, {"$set": {"last_login": datetime.utcnow()}})


# ─────────────────────────────────────────────
# VerificationCode
# ─────────────────────────────────────────────
class VerificationCode:
    @staticmethod
    def create(email):
        code = str(randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        # Remove códigos antigos do mesmo email
        verification_codes_col.delete_many({"email": email})
        verification_codes_col.insert_one({
            "email": email,
            "code": code,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        })
        return code

    @staticmethod
    def verify(email, code):
        doc = verification_codes_col.find_one({
            "email": email,
            "code": code,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        if doc:
            verification_codes_col.delete_many({"email": email})
            return True
        return False


# ─────────────────────────────────────────────
# BlogCategory
# ─────────────────────────────────────────────
class BlogCategory:
    def __init__(self, doc):
        self.id = str(doc["_id"])
        self.name = doc["name"]
        self.description = doc.get("description", "")
        self.created_at = doc.get("created_at")

    @staticmethod
    def get_all():
        return [BlogCategory(d) for d in blog_categories_col.find()]

    @staticmethod
    def get_by_id(category_id):
        try:
            doc = blog_categories_col.find_one({"_id": ObjectId(category_id)})
            return BlogCategory(doc) if doc else None
        except Exception:
            return None

    @classmethod
    def create(cls, name, description=""):
        doc = {
            "name": name,
            "description": description,
            "created_at": datetime.utcnow()
        }
        result = blog_categories_col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return cls(doc)


# ─────────────────────────────────────────────
# Blog
# ─────────────────────────────────────────────
class Blog:
    def __init__(self, doc):
        self.id = str(doc["_id"])
        self.title = doc["title"]
        self.content = doc["content"]
        self.category_id = str(doc["category_id"])
        self.author_id = str(doc["author_id"])
        self.status = doc.get("status", "draft")
        self.created_at = doc.get("created_at")
        self.updated_at = doc.get("updated_at")
        # categoria populada se presente
        cat_doc = doc.get("_category")
        self.category = BlogCategory(cat_doc) if cat_doc else None

    @staticmethod
    def _enrich(doc):
        """Popula a categoria dentro do documento."""
        if doc:
            cat = blog_categories_col.find_one({"_id": doc.get("category_id")})
            doc["_category"] = cat
        return doc

    @staticmethod
    def get_all(status=None):
        query = {}
        if status:
            query["status"] = status
        docs = list(blogs_col.find(query).sort("created_at", -1))
        return [Blog(Blog._enrich(d)) for d in docs]

    @staticmethod
    def get(blog_id):
        try:
            doc = blogs_col.find_one({"_id": ObjectId(blog_id)})
            return Blog(Blog._enrich(doc)) if doc else None
        except Exception:
            return None

    @staticmethod
    def get_by_category(category_id, status="published"):
        try:
            query = {"category_id": ObjectId(category_id)}
            if status:
                query["status"] = status
            docs = list(blogs_col.find(query).sort("created_at", -1))
            return [Blog(Blog._enrich(d)) for d in docs]
        except Exception:
            return []

    @classmethod
    def create(cls, title, content, category_id, author_id, status="draft"):
        now = datetime.utcnow()
        doc = {
            "title": title,
            "content": content,
            "category_id": ObjectId(category_id),
            "author_id": author_id,
            "status": status,
            "created_at": now,
            "updated_at": now
        }
        result = blogs_col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return cls(Blog._enrich(doc))

    def save(self):
        self.updated_at = datetime.utcnow()
        blogs_col.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {
                "title": self.title,
                "content": self.content,
                "category_id": ObjectId(self.category_id),
                "status": self.status,
                "updated_at": self.updated_at
            }}
        )

    def delete(self):
        blogs_col.delete_one({"_id": ObjectId(self.id)})