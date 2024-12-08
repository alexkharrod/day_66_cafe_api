from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, HiddenField
from wtforms.validators import DataRequired
import os
from load_dotenv import load_dotenv
import requests

load_dotenv()

TMDB_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_TOKEN = os.environ.get('TMDB_TOKEN')
TMDB_APIKEY = os.environ.get('TMDB_APIKEY')
TMDB_POSTER_PATH = "https://image.tmdb.org/t/p/w500"
TMDB_MOVIE_DATA_URL = 'https://api.themoviedb.org/3/movie/'

def get_movie_list(title):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }
    params = {
        "query": title,
        "include_adult": False
    }
    #query=matrix&include_adult=false&language=en-US&page=1"
    response = requests.get(TMDB_URL, headers=headers, params=params)
    movies = response.json()
    return movies['results']

def get_movie_data(movie_id):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }
    response = requests.get(f"{TMDB_MOVIE_DATA_URL}{movie_id}", headers=headers)
    movie = response.json()
    return movie


app = Flask(__name__)
Bootstrap5(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


# CREATE DB
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE
class Movie(db.Model):
     id: Mapped[int] = mapped_column(Integer, primary_key=True)
     title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
     year: Mapped[int] = mapped_column(Integer, nullable=False)
     description: Mapped[str] = mapped_column(String(250),  nullable=False)
     rating: Mapped[float]  = mapped_column(Float)
     ranking: Mapped[int] = mapped_column(Integer)
     review:  Mapped[str] = mapped_column(String(200))
     img_url: Mapped[str] = mapped_column(String(90), nullable=False)

# create the form
class MyForm(FlaskForm):
    id = HiddenField()
    rating =  FloatField("Your Rating out of 10, e.g: 7.5", default=1.0, validators=[DataRequired()])
    review = StringField("Your Review", default='My Movie Review', validators=[DataRequired()])
    submit = SubmitField(label="Post Changes")


with app.app_context():
   db.create_all()


@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.rating.desc()))
    movies = result.scalars().all()
    i = 1
    for movie in movies:
        ranking = i
        movie.ranking = ranking
        i += 1
        db.session.commit()
    return render_template("index.html", movies=movies)

@app.route('/select', methods=["POST", "GET"])
def select():
    title = request.args.get('title', default='', type=str)
    movie_list = get_movie_list(title)
    if request.method == 'POST':
        return redirect(url_for('create'))
    return render_template("select.html", movie_list=movie_list)


@app.route('/create/<movie_id>', methods=["POST", "GET"])
def create(movie_id):
    movie = get_movie_data(movie_id)
    id_to_pass = str(movie_id)
    print(id_to_pass)
    print(int(id_to_pass))

    movie_toadd  = Movie(
        title=movie['title'],
        year=movie['release_date'][0:4],
        description=movie['overview'],
        img_url=f"{TMDB_POSTER_PATH}{movie['poster_path']}",
        rating=0,
        ranking=0,
        review=""
    )
    db.session.add(movie_toadd)
    db.session.commit()

    return redirect(url_for('edit',  id=movie_toadd.id))



@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        title = request.form.get('title')
        return redirect(url_for('select', title=title))

    return render_template('add.html')


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    movie_id = int(request.args.get('id'))
    movie_to_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    edit_form = MyForm()
    movie_id = int(request.args.get('id'))
    movie_to_update = db.get_or_404(Movie, movie_id)
    if edit_form.validate_on_submit():
        movie_to_update.rating = edit_form.rating.data
        movie_to_update.review = edit_form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html',form=edit_form, movie=movie_to_update )


if __name__ == '__main__':
    app.run(debug=True)
