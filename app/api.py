from app import db, limiter, limiter
from flask_restful import Resource
from flask import request
from sqlalchemy import func
from .model import Acab, AcabSchema
from .limiters import vote_limiter
import random


acabSchema = AcabSchema(many=True)

class RandomPoemAPI(Resource):
    def get(self):
        rand = random.randint(1,100)
        if (rand > 80) and (len(Acab.query.all()) > 0):
            if (rand > 90):
                acab = Acab.query.order_by(func.random()).first()
                gen = { 'c' : acab.c, 'b' : acab.b, 'votes' : acab.vote,
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

        return { 'gen' : gen }


class ListPoemAPI(Resource):
    def get(self, page = 1):
        pagination = Acab.query.order_by(Acab.vote.desc()).paginate(page,20)
        res = {
            'items'     : acabSchema.dump(pagination.items).data,
            'pagination' : {
                'page'      : pagination.page,
                'pages'     : pagination.pages,
                'has_next'  : pagination.has_next,
                'has_prev'  : pagination.has_prev,
                'next_num'  : pagination.next_num,
                'prev_num'  : pagination.prev_num,
            },
        }
        return res

class VotePoemAPI(Resource):
    decorators = [limiter.limit("1 per day", key_func = lambda : vote_limiter(request) )]
    def post(self):
        content = request.get_json(silent=True)
        if ((u'b' in content) and (u'c' in content)):
            c = content.get(u'c')
            b = content.get(u'b')
        else:
            return { 'error' : "Trying to vote for nothing. What are you? An anarchist?!"}
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
            return { 'vote' : { 'c' : c, 'b' : b }}
        else:
            return { 'error' : "You can't vote for that!"}
