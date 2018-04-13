from app import db, ma

class Acab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    c = db.Column(db.String(32), nullable=False)
    b = db.Column(db.String(22), nullable=False)
    vote = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<all %r are %r>' % (self.c, self.b)

class AcabSchema(ma.ModelSchema):
    class Meta:
        model = Acab
