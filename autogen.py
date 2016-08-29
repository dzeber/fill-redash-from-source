import sys, os
import argparse
import time
import pprint
import yaml
from utils import RequestHandler

base_url = "https://sql.telemetry.mozilla.org/api/"
recheck_frequency = 1

def check_or_update_list(queries, handler):
    datasources = handler.api_get('data_sources')
    dsmap = {}
    for ds in datasources:
        dsmap[ds['name']] = ds

    def check_or_update_query(q):
        id = q['id']
        name = q['name']
        ds = q['data_source']
        qs = q['query']
        schedule = q['schedule']
        api_key = q['api_key']

        updates = {}

        r = handler.api_get('queries', id)
        if r['name'] != name:
            updates['name'] = name
        if r['data_source_id'] != dsmap[ds]['id']:
            updates['data_source_id'] = dsmap[ds]['id']
        if r['query'] != qs:
            updates['query'] = qs
        if r['api_key'] != api_key:
            raise ValueError("API key for query [{}]: {} doesn't match.".format(id, name))
        if r['schedule'] != schedule:
            updates['schedule'] = schedule

        if not len(updates):
            print "[{}] {}: Up to date".format(id, name)
            return

        # If the query has changed, we need to generate a new result set
        # and then associate it with the query
        if 'query' in updates:
            r = handler.api_post({
                'data_source_id': dsmap[ds]['id'],
                'max_age': 0,
                'query': qs,
                'query_id': id
            }, 'query_results')
            job_id = r['job']['id']
            print "[{}] Updating query: status at {}job/{}".format(id, base_url, job_id)
            while r['job']['status'] in (1, 2):
                time.sleep(recheck_frequency)
                r = handler.api_get('jobs', job_id)
                print "*",
                sys.stdout.flush()
            print
            if r['job']['status'] != 3:
                raise ValueError("[{}] {}: new query failed.\n{}".format(id, name, pprint.pformat(r)))
            updates['latest_query_data_id'] = r['job']['query_result_id']
            # do I need to update query_hash? updates['query_hash'] = r['

        print "[{}] {}: Updating {}".format(id, name, ','.join(updates.keys()))
        handler.api_post(updates, 'queries', id)

    for q in queries:
        check_or_update_query(q)

if __name__ == "__main__":
    a = argparse.ArgumentParser(
        description="Update sql.telemetry.mozilla.org queries")
    a.add_argument("manifest",
        metavar="manifest.yaml",
        help="Path to YAML file specifying queries")
    a.add_argument("apikey",
        help="Your sql.telemetry.mozilla.org API key, either the key itself" +
            " or a single-line file containing the key (with the --keyfile" +
            " option)")
    a.add_argument("--keyfile", "-k",
        action="store_true",
        help="Interpret the apikey arg as the path to a single-line file" +
            " containing the key")
    args = a.parse_args()
    if args.keyfile:
        ## Read the API key from the specified file
        try:
            with open(args.apikey) as f:
                apikey = f.read().strip()
            args.apikey = apikey
        except IOError:
            print("Unable to read API key from file.")
            sys.exit(1)

    d = yaml.load(open(args.manifest))
    api_handler = RequestHandler(args.apikey)
    check_or_update_list(d['queries'], api_handler)
