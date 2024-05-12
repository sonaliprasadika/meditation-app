"""
    This module is for test funstionalities of Song reaource
"""
import json
from jsonschema import validate
from werkzeug.datastructures import Headers

RESOURCE_URL = '/api/meditation/'

def test_get_all_songs(client):
    """
        Test get all request 
    """
    #get all songs
    response = client.get(RESOURCE_URL)
    assert response.status_code == 200

    data = json.loads(response.data)
    assert len(data['song list']) == 4
    
def test_get_song(client):
    """
        Test get request 
    """
    # get song with id 5
    response = client.get(f'{RESOURCE_URL}5/')
    assert response.status_code == 204

    data = json.loads(response.data)
    # _check_namespace(client, data)
    # _check_control_get_method("custWorkoutPlaylistGen:collection", client, data)
    # _check_control_put_method("custWorkoutPlaylistGen:edit", client, data)
    # _check_control_delete_method("custWorkoutPlaylistGen:delete", client, data)
    assert data['song_id'] == 1
    assert data["song_name"] == "test-song-1"

def _check_namespace(client, response):
    """
    Checks that the "meditationService" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """

    ns_href = response["@namespaces"]["meditationService"]["name"]
    print(ns_href)
    resp = client.get(ns_href)
    assert resp.status_code == 200

def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    print(href)
    assert resp.status_code == 200