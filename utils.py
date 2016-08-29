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


    def get_data_sources_by_name(self):
        """ Returns a mapping of known data sources keyed by name. """
        datasources = self.api_get("data_sources")
        dsmap = {}
        for ds in datasources:
            dsmap[ds["name"]] = ds
        return dsmap

    def get_data_sources_by_id(self):
        """ Returns a mapping of known data sources keyed by ID. """
        datasources = self.api_get("data_sources")
        dsmap = {}
        for ds in datasources:
            dsmap[ds["id"]] = ds
        return dsmap


def remove_vis_dates(v):
    """ Remove dates from the visualization description returned by the API. """
    del v["created_at"]
    del v["updated_at"]
    return v


def format_vis_for_manifest(visualizations):
    """ Convert the visualization listing for a query returned by the API
        into the format that will get written to the manifest.

        We only need to record the information necessary to recreate the
        visualization. Dates of creation and update are removed. Also,
        visualizations of type "TABLE" are ignored, since they are the default.
    """
    visualizations = filter(lambda v: v["type"] != "TABLE", visualizations)
    visualizations = map(remove_vis_dates, visualizations)
    return visualizations


def block_multiline_string_representer(dumper, data):
    """ Represent multi-line strings in block style.

        CF http://stackoverflow.com/a/33300001
    """
    ## Check for multiline string.
    if len(data.splitlines()) > 1:
        ## If any of the lines have trailing spaces, the string will
        ## not get printed in block style.
        ## If the Emitter will not allow block style output, print a
        ## warning.
        if not dumper.analyze_scalar(data).allow_block:
            print("The following multi-line string will not be printed" +
                " in block style - check that no lines have trailing" +
                " spaces.\n" + repr(data))
        return dumper.represent_scalar('tag:yaml.org,2002:str', data,
            style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

