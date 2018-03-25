from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///acab.db'
db = SQLAlchemy(app)
CORS(app)
limiter = Limiter(app)


class Acab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    c = db.Column(db.String(32), nullable=False)
    b = db.Column(db.String(22), nullable=False)
    vote = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<all %r are %r>' % (self.c, self.b)


def vote_limiter(request):
    content = request.get_json(silent=True)
    if ((u'b' in content) and (u'c' in content)):
        down = False
        if (u'downvote' in content):
            down = content.get('downvote')
        c = content.get('c')
        b = content.get('b')
        return (get_remote_address() + b + c + str(down))


@app.route('/random')
@limiter.exempt
def index():
    if (random.randint(1,10) > 9) and (len(Acab.query.all()) > 0):
        if (random.randint(0,1) == 1):
            acab = Acab.query.order_by(func.random()).first()
            gen = { 'c' : acab.c, 'b' : acab.b,
                    'source' : "a random ACAB chosen from the DB"}
        else:
            c = Acab.query.order_by(func.random()).first().c
            b = Acab.query.order_by(func.random()).first().b
            gen = { 'c' : c, 'b' : b,
                    'source' : 'a random C and B chosen from the DB'}
    else:
        with open('words/c.words', 'r') as f:
            cs = f.readlines()
        with open('words/b.words', 'r') as f:
            bs = f.readlines()
        gen = { 'c' : random.choice(cs).rstrip(), 'b' : random.choice(bs).rstrip(),
                'source' : 'a random C and B chosen from the wordlist'}

    if (('oldc' in request.args) and ('oldb' in request.args)):
        old_c = request.args.get('oldc')
        old_b = request.args.get('oldb')
        gen.update({'old_c' : old_c, 'old_b' : old_b})

    return jsonify(gen = gen)


@app.route('/vote', methods = ['POST'])
# Allow 1 request per day per ip per acab
@limiter.limit("1 per day", key_func = lambda : vote_limiter(request) )
def vote():
    content = request.get_json(silent=True)
    if ((u'b' in content) and (u'c' in content)):
        c = content.get(u'c')
        b = content.get(u'b')
    else:
        return jsonify(error = "Trying to vote for nothing. What are you? An anarchist?!")
    if (('downvote' in content) and (content.get(u'downvote'))):
        multiplier = -1
    else:
        multiplier = 1
      
    if b.startswith('b') and c.startswith('c'):
        acab = Acab.query.filter_by(b=b, c=c).first()
        if acab is None:
            acab = Acab(b=b, c=c, vote=multiplier)
            db.session.add(acab)
            db.session.commit()
        else:
            acab.vote += 1 * multiplier
            db.session.commit()
        return jsonify(vote = { 'c' : c, 'b' : b })
    else:
        return jsonify(error = "You can't vote for that!")


@app.route('/list')
@limiter.exempt
def list():
    acabs = [
        { 'c' : a.c, 'b' : a.b, 'votes' : a.vote }
        for a in Acab.query.order_by(Acab.vote).all()]
    acabs.reverse()
    return jsonify(lst = acabs)


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error = "Please wait a while before you vote for the same thing again")
