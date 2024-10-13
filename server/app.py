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
        response_body = {
            "message" : "Welcome to the lateshow."
        }
        return make_response(jsonify(response_body), 200)

class Episodes(Resource):
    def get(self):
        response_dict_list = [ep.to_dict(rules=('-appearances',)) for ep in Episode.query.all()]
        return make_response(jsonify(response_dict_list), 200)

class EpisodesById(Resource):
    def get(self, id):
        episode = Episode.query.filter_by(id = id).first()
        if episode:
            response_dict = episode.to_dict()
            return make_response(jsonify(response_dict), 200)
        else:
            response_body = {
                "error" : "Episode not found"
            }
            return make_response(jsonify(response_body), 404)

class Appearances(Resource):
    def post(self):
        data = request.json
        new_appearance = Appearance(
            rating = data.get('rating'),
            episode_id = data.get('episode_id'),
            guest_id = data.get('guest_id')
        )
        try:
            db.session.add(new_appearance)
            db.session.commit()
            response_dict = new_appearance.to_dict()
            return make_response(jsonify(response_dict), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": ["Validation errors"]}), 422)

api.add_resource(Home, '/')
api.add_resource(Episodes, '/episodes')
api.add_resource(EpisodesById, '/episodes/<int:id>')
api.add_resource(Appearances, '/appearances')

if __name__ == '__main__':
    app.run(port=5555, debug=True)