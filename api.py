from flask import Blueprint
from flask_restful import Api
from resources.meditation import MeditationResource, SongResource

# Initialize Blueprint and API
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Add resources to the API
api.add_resource(MeditationResource, '/meditation')
api.add_resource(SongResource, '/song/<string:song_id>')  # Ensure proper variable type is defined
