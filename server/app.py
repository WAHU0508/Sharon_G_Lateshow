from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Episode, Appearance, Guest

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lateshow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Home(Resource):
    def get(self):
        """Home route"""
        response_body = {
            "message" : "Welcome to the lateshow."
        }
        return make_response(jsonify(response_body), 200)

class Episodes(Resource):
    def get(self):
        """Get all episodes"""
        response_dict_list = [ep.to_dict(rules=('-appearances',)) for ep in Episode.query.all()]
        return make_response(jsonify(response_dict_list), 200)

class EpisodesById(Resource):
    def get(self, id):
        """Get an episode by it's id"""
        episode = Episode.query.filter_by(id = id).first()
        if episode:
            response_dict = episode.to_dict()
            return make_response(jsonify(response_dict), 200)
        else:
            response_body = {
                "error" : "Episode not found"
            }
            return make_response(jsonify(response_body), 404)

class Guests(Resource):
    def get(self):
        """Get all guests"""
        response_dict_list = [guest.to_dict(rules=('-appearances',)) for guest in Guest.query.all()]
        return make_response(jsonify(response_dict_list), 200)

class Appearances(Resource):
    def post(self):
        """Post a new appearance"""
        data = request.json
        rating = data.get('rating')
        episode_id = data.get('episode_id')
        guest_id = data.get('guest_id')

        episode = Episode.query.filter_by(id = episode_id).first()
        guest = Guest.query.filter_by(id = guest_id).first()

        if not episode or not guest:
            return make_response(jsonify({"errors": ["Episode or guest not found."]}), 404)
        if not 1 <= rating <= 5:
            return make_response(jsonify({"errors": ["Validation errors"]}), 422)

        new_appearance = Appearance(
            rating = rating,
            episode_id = episode_id,
            guest_id = guest_id
        )
        db.session.add(new_appearance)
        db.session.commit()
        response_dict = new_appearance.to_dict()
        return make_response(jsonify(response_dict), 201)

api.add_resource(Home, '/')
api.add_resource(Episodes, '/episodes')
api.add_resource(EpisodesById, '/episodes/<int:id>')
api.add_resource(Guests, '/guests')
api.add_resource(Appearances, '/appearances')

if __name__ == '__main__':
    app.run(port=5555, debug=True)