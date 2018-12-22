from animator import db


class Siteuser(db.Model):
    __tablename__ = 'siteuser'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.name = username
        self.password = password

    def __repr__(self):
        return '<Siteuser {}>'.format(self.username)

    def serialize(self):
        return {
            'id': self.id,
            'username': self.name,
            'password': self.author,
        }


class Profile(db.Model):
    __tablename__ = 'profile'

    id = db.Column(db.Integer, primary_key=True)
    mal_username = db.Column(db.String())
    list = db.Column(db.String(), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('siteuser.id'))

    def serialize(self):
        return {
            'id': self.id,
            'mal_username': self.mal_username,
            'list': self.list,
            'profile_id': self.profile_id
        }


class Recommendations(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    anime_type = db.Column(db.String())
    episodes = db.Column(db.String())
    studio = db.Column(db.String())
    src = db.Column(db.String())
    genre = db.Column(db.String())
    score = db.Column(db.String())
    synopsis = db.Column(db.String())
    url = db.Column(db.String())
    image_url = db.Column(db.String())
    profile_id = db.Column(db.Integer, db.ForeignKey('siteuser.id'))

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'anime_type': self.anime_type,
            'episodes': self.episodes,
            'studio': self.studio,
            'src': self.src,
            'genre': self.genre,
            'score': self.score,
            'synopsis': self.synopsis,
            'url': self.url,
            'image_url': self.image_url,
            'prifile_id': self.profile_id,
        }
