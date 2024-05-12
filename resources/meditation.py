"""
    This module responsible for handling functions related to meditation resource
"""
from __init__ import cache
import json
from flask import Flask, jsonify, request, Response, json, url_for, g
import requests
from werkzeug.exceptions import BadRequest
from flask_restful import Api, Resource
import requests
from config import SERVER_ADDRESS, MASON, ERROR_PROFILE, LINK_RELATION, CONTENT_TYPE

class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href

class MeditationBuilder(MasonBuilder):
    """
        A class for building meditation MASON hypermedia representations.
    """
    def add_control_get_song(self, song_id):
        """
            Adds a control to get a song by its ID.
        """
        self.add_control(
            "item",
            href=f"/meditation/{song_id}",
            method="GET",
            title="Get Song by song_id"
        )

def create_error_response(status_code, title, message=None):
    """
        Creates an error response with a MASON hypermedia representation.
    """
    body = MeditationBuilder()
    body.add_error(title, message if message else "")
    return Response(json.dumps(body), status_code, mimetype=MASON)

class SongCollectionResource(Resource):
    """
        This resource is for calling GET all songs endpoint and returns them in a list format after filtering by song genre.

        Args:
            song genre: song genre is sent as body parameter and is used to filter the song list 
            which belongs to particular genre.

        Returns:
            List of songs containing song details and a controller for each song to get the 
            corresponding song by song ID.
    """
    @cache.cached(timeout=60)
    def get(self):
        
        if not request.data: 
            return create_error_response(400, "Empty request body")
        
        try:
            data = request.get_json(force=True)
        except Exception as e:
            return create_error_response(400, "Failed to decode JSON object")

        song_genre = data.get("song_genre")
        api_key = request.headers.get('X-API-Key')  
        content_type = request.headers.get('Content-Type')
        
        if not api_key:
            return create_error_response(401, "API key is missing")
        
        if content_type != CONTENT_TYPE:
            return create_error_response(415, "Unsupported Media Type", "This service requires JSON input.")
        
        headers = {
            "Content-Type": content_type,
            "X-API-Key": api_key
        }
    
        try:
            updated_songs_list = []
            response = requests.get(f'{SERVER_ADDRESS}/api/song', headers=headers)

            if response.status_code == 200:
                songs_data = response.json()
                
                meditation_plan = MeditationBuilder()
                meditation_plan.add_namespace("meditationService", LINK_RELATION)
                
                songs_list = songs_data['song list']
                
                cleaned_songs_list = [
                    {key: song[key] for key in song if key != '@controls'}
                    for song in songs_list
                ]

                for song in cleaned_songs_list:
                    if song_genre == song['song_genre']:
                        song_dict = MeditationBuilder() 
                        song_dict.update({
                            "song_id": song['song_id'],
                            "song_name": song['song_name'],
                            "song_artist": song['song_artist'],
                            "song_genre": song['song_genre'],
                            "song_duration": song['song_duration']
                        })
                        song_dict.add_control_get_song(song['song_id'])
                        updated_songs_list.append(song_dict)
                
                meditation_plan ["songs" ] = updated_songs_list

                return Response(json.dumps(meditation_plan), status=200, mimetype=MASON)
            else:
                return create_error_response(404, "Failed to retrieve songs", str(e))
        except requests.RequestException as e:
            return create_error_response(500, "Internal server error", str(e))

class SongResource(Resource):
    """
        This resource is for calling the endpoint to GET a song by given song ID and returns details in a list format.

        Returns:
            It contains list of dictionaries representing song details and hypermedia link relations. 
    """
    # @cache.cached(timeout=60)
    def get(self, song_id):
        
        api_key = request.headers.get('X-API-Key') 
        content_type = request.headers.get('Content-Type')
        
        if not api_key:
            return create_error_response(401, "API key is missing")
        
        if content_type != CONTENT_TYPE:
            return create_error_response(415, "Unsupported Media Type", "This service requires JSON input.")
        
        headers = {
            "Content-Type": content_type,
            "X-API-Key": api_key
        }
        
        try:
            response = requests.get(f'{SERVER_ADDRESS}/api/song/{song_id}', headers=headers)

            if response.status_code == 200:
                song_data = response.json()
                return song_data, 200
        except requests.RequestException as e:
            return create_error_response(500, "Internal server error", str(e))


