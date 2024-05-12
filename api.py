from flask import Blueprint
from flask_restful import Api
from resources.meditation import SongCollectionResource, SongResource

# Initialize Blueprint and API
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Add resources to the API
api.add_resource(SongCollectionResource, '/meditation')
api.add_resource(SongResource, '/meditation/<string:song_id>')  # Ensure proper variable type is defined
