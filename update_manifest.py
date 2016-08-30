import sys, os, json
import time
import pprint
import yaml
import utils

def check_or_update_list(query_ids, manifest_queries, handler):
    dsmap = handler.get_data_sources_by_id()

    def check_or_update_query(qid):
        r = handler.api_get('queries', qid)
        new_info = {
            "id": qid,
            "name": r["name"],
            "data_source": dsmap[r["data_source_id"]]["name"],
            "schedule": r["schedule"],
            "api_key": r["api_key"],
            "query": r["query"],
            "description": r["description"],
            "visualizations": utils.format_vis_for_manifest(r["visualizations"])
        }

        ## If this query already has a listing in the manifest, update it.
        ## Otherwise, add it.
        old_info = filter(lambda q: q["id"] == new_info["id"], manifest_queries)
        if old_info:
            old_info = old_info[0]
            if old_info == new_info:
                print("[{}] {}: Up to date".format(new_info["id"], new_info["name"]))
            else:
                if new_info["api_key"] != old_info["api_key"]:
                    raise ValueError("API key for query [{}]: {} doesn't match.".format(id, name))
                updated_info = filter(lambda (k, v): old_info.get(k) != v,
                    new_info.items())
                old_info.update(updated_info) 
                print("[{}] {}: Updated {}".format(new_info["id"],
                    new_info["name"],
                    ", ".join(map(lambda v: v[0], updated_info))))
        else:
            manifest_queries.append(new_info)
            print("[{}] {}: Added to the manifest".format(new_info["id"],
                new_info["name"]))

    for q in query_ids:
        check_or_update_query(q)
    return manifest_queries


if __name__ == "__main__":
    arg_parser = utils.QuerySyncArgParser("Update or generate YAML" +
        " manifest specifying re:dash (sql.telemetry.mozilla.org) queries")
    arg_parser.add_argument("query_ids",
        nargs= "*",
        metavar="queryID",
        type=int,
        help="IDs of the queries to write to the YAML manifest. If a query" +
            " is already listed in the manifest, its entry will get updated." +
            " Otherwise the query will be added to the file. If no queries" +
            " are specified, all queries in the manifest will be updated.")
    try:
        args = arg_parser.parse_args()
    except IOError:
        ## The key file was not readable, and a message was already printed.
        print("Exiting...")
        sys.exit(1)

    try:
        mf_queries = yaml.load(open(args.manifest))
        mf_queries = mf_queries["queries"]
    except (IOError, KeyError):
        ## File does not yet exist or does not contain a "queries" block.
        mf_queries = []
    query_ids = args.query_ids
    if not query_ids:
        ## No queries specified. Use the ones listed in the file, if any.
        if not mf_queries:
            print("No queries to update. Exiting...")
            sys.exit()
        query_ids = map(lambda q: q["id"], mf_queries)
    api_handler = utils.RequestHandler(args.apikey)
    new_mf_queries = check_or_update_list(query_ids, mf_queries, api_handler)
    ## Wrap the list of queries inside a top-level mapping.
    new_mf_queries = { "queries": new_mf_queries }

    ## Use safe_dump to avoid tagging Python object types.
    ## In particular, treat unicode as str.
    ## Use custom string representer to print multi-line strings in block style.
    yaml.SafeDumper.add_representer(str,
        utils.block_multiline_string_representer)
    yaml.SafeDumper.add_representer(unicode,
        utils.block_multiline_string_representer)
    yaml.safe_dump(new_mf_queries, open(args.manifest, "w"))
