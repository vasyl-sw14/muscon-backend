from flask import Flask, g, jsonify, request, render_template, make_response
import spotipy
from rich.markup import render
from spotipy.oauth2 import SpotifyClientCredentials
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
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


@app.route('/login', methods=['POST'])
@auth.verify_password
def login():
    data = request.get_json()
    user = User(
        username=data['username'],
        password=bcrypt.generate_password_hash(
            data['password']).decode('utf-8'),
    )
    user = session.query(User).filter(
        User.username == data['username']).one_or_none()
    if user is None:
        return 'User with such username was not found'

    if not bcrypt.check_password_hash(user.password, data['password']):
        return 'Wrong password'

    access_token = create_access_token(identity=user.id)

    return jsonify({'token': access_token})


@app.route('/genres', methods=['GET'])
def get_genres():
    result = sp.recommendation_genre_seeds()
    return jsonify(result['genres'])


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
def add_song_for_user(user_id, song_id):
    user = session.query(User).filter(User.id == user_id).one_or_none()
    if user is None:
        return 'User not found', '404'

    if user.track_id!=None:
        for track in user.track_id:
            if track==song_id:
                return jsonify({'message':'You already added that song'})
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

    #if not session.query(Wall).filter(Wall.user_id != data['user_id']).one_or_none() is None:
     #   return 'Such user doesn\'t exist', '400'

    if not session.query(User).filter(Wall.genre_id != data['genre_id']).one_or_none() is None:
        return 'Such genre doesn\'t exist', '400'

    session.add(new)
    session.commit()

    return jsonify({'message': 'successful operation!'})


@app.route('/news', methods=['GET'])
@jwt_required()
def display_news(id=all):
    get_news = session.query(User).filter(Wall.id == id).all()
    wall_schema = WallSchema()
    if get_news is None:
        return 'There wasn`t any news yet'
    return jsonify(get_news)


@app.route('/friends', methods=['GET'])
@jwt_required()
def suggested_friends(username=all):
    find_user = session.query(User).filter(User.username == username).all()
    user_schema = UserSchema()
    return jsonify('You may like: ', find_user)


@app.route('/edit_genre', methods=['POST'])
@jwt_required()
def edit_genre():
    current_user = get_jwt_identity()
    if current_user is None:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    data = request.get_json()
    edit_profile = Genre(
        name=data['name_of_genre']
    )

    if not session.query(Genre).filter(Genre.name != data['name_of_genre']).one_or_none() is None:
        return 'There isn`t such genre in our base', '400'

    session.add(edit_genre)
    session.commit()

    return jsonify({'message': 'your data was changed'})


@app.route('/edit_artist', methods=['POST'])
@jwt_required
def edit_artist():
    current_user = get_jwt_identity()
    if current_user is None:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    data = request.get_json()
    edit_profile = Artist(
        name=data['name_of_artist']
    )

    if not session.query(Artist).filter(Artist.name != data['name_of_artist']).one_or_none() is None:
        return 'There isn`t such artist in our base', '400'

    session.add(edit_artist)
    session.commit()

    return jsonify({'message': 'your data was changed'})


@app.route('/<id>/<friend>', methods=['POST'])
@jwt_required()
def send_friend_request(id, friend):
    current_user_id = get_jwt_identity()
    if int(id)!=current_user_id:
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
    if int(id)!=current_user_id:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    find_user = session.query(User).filter(User.username == friend).one_or_none()
    find_friend_1 = session.query(Friends).filter(Friends.user_id_1 == id).filter(
        Friends.user_id_2 == find_user.id).one_or_none()
    find_friend_1.status = 'accepted'

    find_friend_2 = session.query(Friends).filter(Friends.user_id_2 == id).filter(
        Friends.user_id_1 == find_user.id).one_or_none()
    find_friend_2.status = 'accepted'

    session.commit()
    return 'You are friends now!'


@app.route('/<id>/<friend>', methods=['DELETE'])
@jwt_required()
def decline_friend_request(id, friend):
    current_user_id = get_jwt_identity()
    if int(id)!=current_user_id:
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
    if int(id)!=current_user_id:
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
        return 'You are not friends'

    return find_friend


@app.route('/<id>/friends', methods=['GET'])
@jwt_required()
def get_friends(id):
    current_user_id = get_jwt_identity()
    if int(id)!=current_user_id:
        return make_response(jsonify({"403": "Access is denied"}), 403)

    find_friends = session.query(Friends).filter(

        Friends.user_id_1 == id).filter(Friends.status == 'accepted').all()

    if find_friends is None:
        return 'You have no friends'

    return jsonify(find_friends)


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
