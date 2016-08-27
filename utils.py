"""
Utilities for interacting with the re:dash API.
"""

import urllib2
import json

base_url = "https://sql.telemetry.mozilla.org/api/"

class RequestHandler:
    """
    A utility for interacting with the re:dash API via HTTP GET and POST
    requests.
    
    The user's API key is stored on initialization, and wrapped into all
    generated requests.
    """
    def __init__(self, user_api_key):
        self.user_api_key = user_api_key


    def api_get(self, *path):
        """ Generate a GET request with the specified path components.
            
            This is used for downloading query/job metadata, and accessing
            query results.

            Returns the result as a JSON object.
        """
        url = base_url + '/'.join(map(str, path))
        r = urllib2.Request(url)
        r.add_header('Authorization', 'Key ' + self.user_api_key)
        fd = urllib2.urlopen(r)
        return json.load(fd)


    def api_post(self, d, *path):
        """ Generate a POST request with specified JSON data and path
            components.

            This is used for running queries and updating query metadata.

            Returns the result as a JSON object.
        """
        url = base_url + '/'.join(map(str, path))
        r = urllib2.Request(url, json.dumps(d))
        r.add_header('Authorization', 'Key ' + self.user_api_key)
        r.add_header('Content-Type', 'application/json;charset=utf-8')

        try:
            fd = urllib2.urlopen(r)
        except urllib2.HTTPError, e:
            print >>sys.stderr, "HTTP response"
            print >>sys.stderr, e.read()
            raise
        return json.load(fd)

