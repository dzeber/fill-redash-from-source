# fill-redash-from-source

A tool to generate redash queries from a source-controlled, reviewable, pull-requestable repository.

## Usage Instructions

### To log to Mozilla re:dash and find your API key

* Visit https://sql.telemetry.mozilla.org/
* Choose "Log In with Google"
* Log in with your *@mozilla.com address. For privacy reasons, re:dash query access is currently limited to Mozilla employees.
* In the upper right corner choose your name and open settings.
* In the "API Key" tab you can copy your API key. **Keey your API key secret; do not share it with anyone.**

### To modify an existing query:

* Edit autogen.yaml with your changes
* Run `python autogen.py autogen.yaml API_KEY` using your API key from above
    - Alternatively, if your API key is stored in a file (eg. `redash.key`), run `python autogen.py autogen.yaml -k redash.key`
* Unless you are a re:dash admin, you will only be able to make changes to the queries that you created.

### To create a new query

This tool does not make brand-new queries. To create a new query, you create a dummy query in re:dash and then update it using the tool

* Visit https://sql.telemetry.mozilla.org/queries/new
* Choose the data source you need (most queries use the "Presto" datasource)
* Type in a dummy query such as `SELECT TRUE`.
* Choose the "execute" button.
* After the query has finished executing, choose the "Save" button.
* The URL will change to contain the new query ID: https://sql.telemetry.mozilla.org/queries/*id*/source
* Next to the save button is a hamburger menu which has a "Show API Key" menu item. Copy the query API key.
* In `autogen.yaml`, create a new query definition using the query ID and query API key from above.
* It may be useful to prototype the query text in the re:dash UI before copying it to the YAML.

### To sync edits made to a query in the web interface

* Edit the query and visualizations at https://sql.telemetry.mozilla.org/.
* Execute and Save the query.
* Look for the query ID in the URL: https://sql.telemetry.mozilla.org/queries/*id*/source.
* Run `python update_manifest.py autogen.yaml API_KEY QUERY_ID`, or replace `API_KEY` with `-k KEY_FILE` if the API key is to be read from a file.
* This can be used to automatically pull in information for a new query created as above.

The `update_manifest.py` script operates as follows:

* It can be called with one or more query IDs, or with no query IDs, and a YAML file path that may or may not exist.
* If one or more query IDs are given, then for each of these:
    - If a previous version of the query already exists in the YAML, it is updated.
    - Otherwise it is appended.
* If the YAML file does not yet exist, it is created and contains listings for each of the specified queries
* If no query IDs are given, all queries listed in the manifest are updated (in this case, the YAML file must exist).
* Query information that is synced includes the query code, ID, name, description, update schedule, as well as information about any visualizations (excluding the default table output, which is considered a "visualization" in re:dash).
* __Note: the YAML file is overwritten.__

## About API Keys ##

There are two different kinds of API keys in re:dash:

* The **user API key** allows a script to impersonate a user and make changes on their behalf. This is what `autogen.py` uses to update queries. You should keep your user API key secret.
* The **query API key** allows anyone to view a query and query results. You use this API key to publish query results using URLs such as https://sql.telemetry.mozilla.org/api/queries/*id*/results.json?api_key=*query-api-key* (you can also use .csv and .xslx)
