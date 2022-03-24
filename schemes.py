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
    genre_id = fields.Str()
    datetime = fields.Date()
    title = fields.Str()
    text = fields.Str()
    photo_wall = fields.Bool()

    @post_load
    def all_news(self, data, **kwargs):
        return Wall(**data)