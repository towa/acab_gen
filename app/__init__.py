from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///acab.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)
limiter = Limiter(app)


from app.api import ListPoemAPI, RandomPoemAPI, VotePoemAPI

api = Api(app)
api.add_resource(ListPoemAPI, '/list/<int:page>', endpoint = 'list.page')
api.add_resource(ListPoemAPI, '/list', endpoint = 'list')
api.add_resource(RandomPoemAPI, '/random', endpoint = 'random')
api.add_resource(VotePoemAPI, '/vote', endpoint = 'vote')
