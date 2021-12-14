from flask import Flask, g
import sqlite3

app = Flask(__name__)
app.config["DEBUG"] = True

DATABASE = "./test.db"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.route('/', methods=['GET'])
def home():
    print(get_db())
    return "MusCon Backend"


app.run()
