from marshmallow import Schema, fields, validate, post_load
from models import *


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Email(validate=validate.Email())
    password = fields.Str()
    city = fields.Str()
    photo = fields.Bool()

    @post_load
    def all_users(self, data, **kwargs):
        return User(**data)


class WallSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    genre_id = fields.Int()
    datetime = fields.Date()
    text = fields.Str()
    photo_wall = fields.Bool()

    @post_load
    def all_news(self, data, **kwargs):
        return Wall(**data)

class ArtistSchema(Schema):
    id = fields.Int()
    name = fields.Str()

    @post_load
    def all_users(self, data, **kwargs):
        return Artist(**data)

class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()

    @post_load
    def all_users(self, data, **kwargs):
        return Genre(**data)

class TrackSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    artist = fields.Str()

    @post_load
    def all_users(self, data, **kwargs):
        return Genre(**data)