import MySQLdb
from flask import Flask, g, jsonify, request, render_template
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import User, Session, Wall
from flask_httpauth import HTTPBasicAuth


app = Flask(__name__)
app.config["DEBUG"] = True

DATABASE = "./test.db"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="7ed78a10ad33404c952dec000863ec9e",
                                                           client_secret="df0f57a438454795a9b1da87825000de"))
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
auth = HTTPBasicAuth()
session = Session()


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.route('/', methods=['GET'])
def home():
    return "MusCon Backend"


@app.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
        city=data['city'],
        photo=data['photo']
    )

    if not session.query(User).filter(User.username == data['username']).one_or_none() is None:
        return 'This username already exists', '400'

    if not session.query(User).filter(User.email == data['email']).one_or_none() is None:
        return 'This email is taken', '400'

    session.add(new_user)
    session.commit()

    return jsonify({'message': 'successful operation'})


@app.route('/login', methods=['POST'])
@auth.verify_password
def login():
    data = request.get_json()
    user = User(
        username=data['username'],
        password=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
    )
    user = session.query(User).filter(User.username == data['username']).one_or_none()
    if user is None:
        return 'User with such username was not found'

    if not bcrypt.check_password_hash(user.password, data['password']):
        return 'Wrong password'

    return jsonify({'message': 'successful operation'})


@app.route('/genres', methods=['GET'])
def get_genres():
    result = sp.recommendation_genre_seeds()
    print(result)
    return jsonify(result['genres'])


@app.route('/get_artists', methods=['POST'])
def get_artists():
    genres = request.form.get('genres')
    if (genres is None):
        return "Please enter valid data", 400
    artists = []
    result = sp.recommendations(seed_genres=genres.split(', '), limit=20)
    for track in result['tracks']:
        for artist in track['artists']:
            artist_data = sp.artist(artist['uri'])
            if not any(a['name'] == artist_data['name'] for a in artists) and len(artist_data['images']) > 0:
                artists.append(
                    {'name': artist_data['name'], 'image': artist_data['images'][0],
                     'popularity': artist_data['popularity']})
    artists.sort(key=lambda x: x['popularity'], reverse=True)
    return jsonify(artists)


@app.route('/wall', methods=['POST'])
def create_news():
    data = request.get_json()
    new = Wall(
        user_id=data['user_id'],
        username=data['username'],
        photo=data['photo'],
        genre_id=data['genres'],
        datetime=data['date'],
        text=data['string'],
        photo_wall=data['photo']
    )

    if not session.query(Wall).filter(Wall.user_id != data['user_id']).one_or_none() is None:
        return 'There isn`t such user', '400'

    if not session.query(User).filter(Wall.genre_id != data['genre_id']).one_or_none() is None:
        return 'There isn`t such genre', '400'

    session.add(new)
    session.commit()

    return jsonify({'message': 'successful operation!'})


@app.route('/display_news', methods=['GET'])
def display_news():
    db = MySQLdb.connect("127.0.0.1", "root", "Bonia9977", "muscon")
    cursor = db.cursor()
    cursor.execute("SELECT * from wall")
    cursor.fetchall()
    db.close()
    return 'template'


if __name__ == "__main__":
    app.run()
