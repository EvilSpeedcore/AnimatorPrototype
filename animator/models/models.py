from animator import db


class Siteuser(db.Model):
    __tablename__ = 'siteuser'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String())
    age = db.Column(db.Integer())
    country = db.Column(db.String())

    def __repr__(self):
        return '<Siteuser {}>'.format(self.username)


class Profile(db.Model):
    __tablename__ = 'profile'

    id = db.Column(db.Integer, primary_key=True)
    mal_username = db.Column(db.String())
    list = db.Column(db.String(), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('siteuser.id'))


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


class TopAnime(db.Model):
    __tablename__ = 'topanime'

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


class Statistics(db.Model):
    __tablename__ = 'statistics'

    id = db.Column(db.Integer, primary_key=True)
    accepted_anime_number = db.Column(db.Integer())
    denied_anime_number = db.Column(db.Integer())
    profile_id = db.Column(db.Integer, db.ForeignKey('siteuser.id'))
