import sqlite3
from enum import UNIQUE

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, NotNullable


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
db.init_app(app)

class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250),nullable=False)
    rating: Mapped[float] = mapped_column(Float,nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def home():

    book1   = Books(
                id= 2,
                title="Harry Potter",
                author= "J. K. Rowling",
                rating= 9.3
            )
    with app.app_context():
        db.session.add(book1)
        db.session.commit()
    return "Home Page"


if __name__ == "__main__":
    app.run(debug=True)