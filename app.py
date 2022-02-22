from flask import Flask, g, jsonify, request, render_template, make_response
import spotipy
from flask_cors import CORS, cross_origin
from rich.markup import render
from spotipy.oauth2 import SpotifyClientCredentials
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.sql.functions import user

from models import User, Session, Wall, Friends, Genre, Artist, metadata
import MySQLdb
from spotipy.oauth2 import SpotifyClientCredentials
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import User, Wall, Session, Friends
from flask_httpauth import HTTPBasicAuth
from flask_socketio import SocketIO, send, emit
from schemes import UserSchema, WallSchema
import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, JWTManager, get_jwt
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "secret_key"
socketio = SocketIO(app)
CORS(app)

DATABASE = "./test.db"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="7ed78a10ad33404c952dec000863ec9e",
                                                           client_secret="df0f57a438454795a9b1da87825000de"))
bcrypt = Bcrypt(app)
auth = HTTPBasicAuth()
jwt = JWTManager(app)

session = Session()


@socketio.on('message')
def handle_message(data):
    send(data)


@app.route('/', methods=['GET'])
def home():
    return "MusCon Backend"


@app.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=bcrypt.generate_password_hash(
            data['password']).decode('utf-8'),
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


@app.route('/edit_profile', methods=['PUT'])
@jwt_required()
def edit_profile():
    current_user = get_jwt_identity()
    if current_user is None:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    find_user = session.query(User).filter(User.id == current_user).one_or_none()
    if find_user is None:
        return 'User not found'

    data = request.get_json()

    if not session.query(User).filter(User.username == data['username']).one_or_none() is None:
        return 'This username already exists', '400'

    if not session.query(User).filter(User.email == data['email']).one_or_none() is None:
        return 'This email is taken', '400'

    find_user.username = data['username']
    find_user.email = data['email']
    find_user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    find_user.city = data['city']
    find_user.photo = data['photo']

    session.commit()

    return jsonify({'message': 'successful operation'})


@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    if current_user is None:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    find_user = session.query(User).filter(User.id == current_user).one_or_none()
    if find_user is None:
        return 'User not found'

    user_schema = UserSchema()
    user = user_schema.dump(find_user)
    return user


@app.route('/login', methods=['GET'])
@auth.verify_password
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authantication': 'Basic realm:"login require"'})

    user = session.query(User).filter(
        User.username == auth.username).one_or_none()
    if user is None:
        return 'User with such username was not found'

    if not bcrypt.check_password_hash(user.password, auth.password):
        return 'Wrong password'

    access_token = create_access_token(identity=user.id)

    return jsonify({'token': access_token})


@app.route('/genres', methods=['GET'])
def get_genres():
    result = sp.recommendation_genre_seeds()
    return jsonify(result['genres'])


@app.route('/<user_id>/<genre_id>', methods=['POST'])
def add_genre_for_user(user_id, genre_id):
    user.genre_id = []
    user.genre_id.append(genre_id)
    session.commit()

    return jsonify({'message': 'successful operation'})


@app.route('/songs', methods=['POST'])
def get_songs():
    id = request.form.get('id')
    result = sp.artist_top_tracks(id)
    tracks = []
    for track in result['tracks']:
        if (len(track['album']['images']) > 0):
            tracks.append(
                {'id': track['id'], 'name': track['name'], 'image': track['album']['images'][0]})
    return jsonify(tracks)


@app.route('/<user_id>/<song_id>', methods=['PUT'])
@app.route('/songs/<user_id>/<song_id>', methods=['PUT'])
def add_song_for_user(user_id, song_id):
    user = session.query(User).filter(User.id == user_id).one_or_none()
    if user is None:
        return 'User not found', '404'

    if user.track_id != None:
        for track in user.track_id:
            if track == song_id:
                return jsonify({'message': 'You already added that song'})
    else:
        user.track_id = []
    user.track_id.append(song_id)
    session.commit()

    return jsonify({'message': 'successful operation'})


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
                    {'id': artist_data['id'], 'name': artist_data['name'], 'image': artist_data['images'][0],
                     'popularity': artist_data['popularity']})
    artists.sort(key=lambda x: x['popularity'], reverse=True)
    return jsonify(artists)


@app.route('/<user_id>/<artist_id>', methods=['POST'])
def add_artist_for_user(user_id, artist_id):
    user.artist_id = []
    user.artist_id.append(artist_id)
    session.commit()

    return jsonify({'message': 'successful operation'})


@app.route('/wall', methods=['POST'])
@jwt_required()
def create_news():
    current_user = get_jwt_identity()
    if current_user is None:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    data = request.get_json()
    new = Wall(
        user_id=current_user,
        genre_id=data['genre_id'],
        datetime=datetime.utcnow(),
        text=data['text'],
        photo_wall=data['photo']
    )

    if not session.query(User).filter(Wall.genre_id != data['genre_id']).one_or_none() is None:
        return 'Such genre doesn\'t exist', '400'

    session.add(new)
    session.commit()

    return jsonify({'message': 'successful operation!'})


@app.route('/news', methods=['GET'])
@jwt_required()
def display_news():
    current_user = get_jwt_identity()
    if current_user is None:
        return make_response(jsonify({"403": "Access is denied"}), 403)
    data = request.get_json()

    get_news = session.query(User).all()
    news = []
    if get_news is None:
        return 'There wasn`t any news yet'
    return jsonify(news)


@app.route('/friends', methods=['GET'])
@jwt_required()
def suggested_friends():
    current_user = get_jwt_identity()
    if current_user is None:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    find_user = session.query(User).filter(User.id == current_user).one_or_none()
    find_friend = session.query(User).filter(User.genre_id == find_user.genre_id).all()

    user = []
    for friend in find_friend:
        if friend.id != current_user:
            user.append(UserSchema(exclude=['password']).dump(friend))
    return jsonify(user)


@app.route('/edit_genre', methods=['PUT'])
@jwt_required()
def edit_genre():
    current_user = get_jwt_identity()
    if current_user is None:
        return make_response(jsonify({"403": "Access is denied"}), 403)
    data = request.get_json()

    find_user = session.query(User).filter(User.id == current_user).one_or_none()
    if find_user is None:
        return 'error'
    if find_user.genre_id is None:
        find_user.genre_id = data["genre_id"]
    else:
        find_user.genre_id.append(data["genre_id"])

    session.commit()
    return jsonify({'message': 'successful operation'})


@app.route('/edit_artist', methods=['PUT'])
@jwt_required
def edit_artist():
    current_user = get_jwt_identity()
    if current_user is None:
        return make_response(jsonify({"403": "Access is denied"}), 403)
    data = request.get_json()

    find_user = session.query(User).filter(User.id == current_user).one_or_none()
    if find_user is None:
        return 'error'
    if find_user.artist_id is None:
        find_user.artist_id = data["artist_id"]
    else:
        find_user.artist_id.append(data["artist_id"])

    session.commit()
    return jsonify({'message': 'successful operation'})


@app.route('/<id>/<friend>', methods=['POST'])
@jwt_required()
def send_friend_request(id, friend):
    current_user_id = get_jwt_identity()
    if int(id) != current_user_id:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    find_friend = session.query(User).filter(User.username == friend).one_or_none()

    if find_friend is None:
        return 'Such user doesn\'t exist'

    new_friend_1 = Friends(
        user_id_1=id,
        user_id_2=find_friend.id,
        status='new'
    )

    new_friend_2 = Friends(
        user_id_1=find_friend.id,
        user_id_2=id,
        status='new'
    )

    session.add(new_friend_1)
    session.add(new_friend_2)
    session.commit()
    return 'successful request'


@app.route('/<id>/<friend>', methods=['PUT'])
@jwt_required()
def accept_friend_request(id, friend):
    current_user_id = get_jwt_identity()
    if int(id) != current_user_id:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    find_user = session.query(User).filter(User.username == friend).one_or_none()
    find_friend_1 = session.query(Friends).filter(Friends.user_id_1 == id).filter(
        Friends.user_id_2 == find_user.id).one_or_none()
    find_friend_1.status = 'accepted'

    find_friend_2 = session.query(Friends).filter(Friends.user_id_2 == id).filter(
        Friends.user_id_1 == find_user.id).one_or_none()
    find_friend_2.status = 'accepted'

    try:
        session.commit()
    except:
        session.rollback()
    return 'You are friends now!'


@app.route('/<id>/<friend>', methods=['DELETE'])
@jwt_required()
def decline_friend_request(id, friend):
    current_user_id = get_jwt_identity()
    if int(id) != current_user_id:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    find_user = session.query(User).filter(User.username == friend).one_or_none()
    find_friend_1 = session.query(Friends).filter(Friends.user_id_1 == id).filter(
        Friends.user_id_2 == find_user.id).one_or_none()
    find_friend_1.status = 'declined'

    find_friend_2 = session.query(Friends).filter(Friends.user_id_2 == id).filter(
        Friends.user_id_1 == find_user.id).one_or_none()
    find_friend_2.status = 'declined'

    session.commit()
    return 'You are not friends'


@app.route('/<id>/<friend>', methods=['GET'])
@jwt_required()
def get_friend(id, friend):
    current_user_id = get_jwt_identity()
    if int(id) != current_user_id:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    find_user = session.query(User).filter(
        User.username == friend).one_or_none()

    if find_user is None:
        return 'User with such a username doesn\'t exist'

    find_friend = session.query(Friends).filter(Friends.user_id_1 == id).filter(
        Friends.user_id_2 == find_user.id).one_or_none()

    if find_friend is None:
        return 'You don\'t have a friend with such username'

    if find_friend.status != 'accepted':
        return 'You are not friends yet'

    found_friend = session.query(User).filter(User.id == find_friend.user_id_2).one_or_none()
    user = UserSchema(exclude=['password']).dump(found_friend)
    return user


@app.route('/<id>/friends', methods=['GET'])
@jwt_required()
def get_friends(id):
    current_user_id = get_jwt_identity()
    if int(id) != current_user_id:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    find_friends = session.query(Friends).filter(

        Friends.user_id_1 == id).filter(Friends.status == 'accepted').all()

    if find_friends is None:
        return 'You have no friends'
    found_friend = []
    for friend in find_friends:
        found_friend.append(session.query(User).filter(User.id == friend.user_id_2).one_or_none())
    user = []
    for friend in found_friend:
        user.append(UserSchema(exclude=['password']).dump(friend))
    return jsonify(user)


@app.route('/get_top_artists', methods=['POST'])
def get_top_artists():
    genres = request.form.get('genres')
    artists = []
    result = sp.recommendations(seed_genres=genres.split(', '), limit=10)
    for track in result['tracks']:
        for artist in track['artists']:
            artist_data = sp.artist(artist['uri'])
            if not any(a['name'] == artist_data['name'] for a in artists) and len(artist_data['images']) > 0:
                artists.append(
                    {'id': artist_data['id'], 'name': artist_data['name'], 'image': artist_data['images'][0],
                     'popularity': artist_data['popularity']})
    artists.sort(key=lambda x: x['popularity'] == 100, reverse=True)
    return jsonify(artists)


if __name__ == "__main__":
    socketio.run(app)
    app.run()
