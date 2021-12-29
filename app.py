from flask import Flask, g, jsonify, request
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
app.config["DEBUG"] = True

DATABASE = "./test.db"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="7ed78a10ad33404c952dec000863ec9e",
                                                           client_secret="df0f57a438454795a9b1da87825000de"))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.route('/', methods=['GET'])
def home():
    return "MusCon Backend"


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
                    {'name': artist_data['name'], 'image': artist_data['images'][0], 'popularity': artist_data['popularity']})
    artists.sort(key=lambda x: x['popularity'], reverse=True)
    return jsonify(artists)


if __name__ == "__main__":
    app.run()
