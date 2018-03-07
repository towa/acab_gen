from flask import Flask, render_template, request, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///acab.db'
db = SQLAlchemy(app)
limiter = Limiter(app)


class Acab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    c = db.Column(db.String(32), nullable=False)
    b = db.Column(db.String(22), nullable=False)
    vote = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<all %r are %r>' % (self.c, self.b)


@app.route('/')
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
        gen = { 'c' : random.choice(cs), 'b' : random.choice(bs),
                'source' : 'a random C and B chosen from the wordlist'}
    return render_template('index.html', gen = gen)

@app.route('/vote')
# Allow 1 request per day per ip per acab
@limiter.limit("1 per day", key_func = lambda : get_remote_address()
    + request.args.get('b') + request.args.get('c'))
def vote():
    b = request.args.get('b')
    c = request.args.get('c')
    print request.environ['REMOTE_ADDR']
    if b.startswith('b') and c.startswith('c'):
        acab = Acab.query.filter_by(b=b, c=c).first()
        if acab is None:
            acab = Acab(b=b, c=c, vote=1)
            db.session.add(acab)
            db.session.commit()
        else:
            acab.vote += 1
            db.session.commit()
        return redirect(url_for('list'))
    else:
        return render_template('error.html', desc = "You can't vote for that"), 201

@app.route('/list')
@limiter.exempt
def list():
    acabs = [
        { 'c' : a.c, 'b' : a.b, 'votes' : a.vote }
        for a in Acab.query.order_by(Acab.vote).all()]
    acabs.reverse()
    return render_template('list.html', lst = acabs)

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('error.html', desc = "Please wait a while before you vote again"), 429
