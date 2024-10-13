from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Episode(db.Model, SerializerMixin):

    __tablename__ = 'episodes'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    number = db.Column(db.Integer)

    # Relationship mapping the episode to related appearances
    appearances = db.relationship(
        'Appearance', back_populates='episode', cascade='all, delete-orphan')

    # Association proxy to get guests for this episode through appearances
    guests = association_proxy('appearances', 'guest',
                                 creator=lambda guest_obj: Appearance(guest=guest_obj))

    serialize_rules = ('-appearances.episode',)

    def _repr_(self):
        return f'<Episode id: {self.id}, date: {self.date}, number: {self.number}>'

class Appearance(db.Model, SerializerMixin):

    __tablename__ = 'appearances'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    
    # Foreign key to store the episode id
    episode_id = db.Column(db.Integer, db.ForeignKey('episodes.id'))
    # Foreign key to store the guest id
    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'))

    # Relationship mapping the appearance to related episode
    episode = db.relationship('Episode', back_populates='appearances')
    # Relationship mapping the appearance to related guest
    guest = db.relationship('Guest', back_populates='appearances')

    serialize_rules = ('-episode.appearances', '-guest.appearances',)

    @validates('rating')
    def validate_rating(self, key, rating):
        if not 1 <= rating <= 5:
            raise ValueError("The rating should be a value between 1 and 5 inclusive")
        return rating

    def _repr_(self):
        return f'<Appearance id: {self.id}, rating: {self.rating}, episode_id: {self.episode_id}, guest_id: {self.guest_id}>'

class Guest(db.Model, SerializerMixin):

    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    occupation = db.Column(db.String)

    # Relationship mapping the guest to related appearances
    appearances = db.relationship(
        'Appearance', back_populates='guest', cascade='all, delete-orphan')

    # Association proxy to get episodes for this guest through appearances
    episodes = association_proxy('appearances', 'episode',
                                  creator=lambda episode_obj: Appearance(episode=episode_obj))

    serialize_rules = ('-appearances.guest',)

    def _repr_(self):
        return f'Guest id: {self.id}, name: {self.name}, occupation: {self.occupation}'