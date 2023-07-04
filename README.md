# Python Client for Proffix REST API

proffix_api is a lightweight Python package to manage connections to the REST API of [Proffix](https://www.proffix.ch/), an ERP software popular in Switzerland. This package simplifies the interaction with Proffix's API by automatically handling authentication. It is designed as a thin wrapper that routes requests via universal methods and does not implement individual endpoints.

Most GET, POST, PATCH, PUT and DELETE requests are transmitted via generic `get()`, `post()`, `patch()`, `put()` and `delete()` methods. These methods take an API `endpoint`, request parameters and json payload as arguments and return the server's response as a `requests.Response` object.

The package further provides specific methods for endpoints that can not be handled by the generic requests:
- `login()` and `logout()` manage the `session_id` authentication token.
- `info()` and `database()` _class_ methods access PRO/INFO and PRO/DATABASE endpoints. These endpoints require an API key as an authentication token and do not depend on the standard login mechanism.\
_(Note that the api_key is solely needed for these endpoints. All other endpoints can be used without the api_key)._

The Proffix API manages authentication through a `PxSessionId` token transmitted in the HTML header. The token is initially acquired by a html POST request to the PRO/LOGIN endpoint. The proffix_api package embeds the current session ID in the HTML header and obtains a new session ID if none is available or if the current one has expired. A new session ID is acquired through the `login()` method that forwards username, password, database name and necessary modules to the 'PRO/LOGIN' endpoint.

## Installation

```bash
pip install https://github.com/lasuk/proffix_api/tarball/main
```

## Usage

Below example connects to the API [test environment](https://www.proffix.ch/Portals/0/content/REST%20API/zugriff_auf_testumgebung.html) provided by Proffix. Changes can be viewed in the online demo GUI.


```python
import re, pandas as pd
from proffix_api import ProffixAPIClient


# Login ------------------------------------------------------------------------

# Query available databases
ProffixAPIClient.database(
    base_url = "https://remote.proffix.net:11011/pxapi/v4",
    api_key = "Demo_2016_PWREST!,Wangs")

# Connect to test environment
proffix = ProffixAPIClient(
    base_url = "https://remote.proffix.net:11011/pxapi/v4",
    username = "Gast",
    password = "gast123",
    database = "DEMODB",
    modules = ["VOL"])


# Contacts ---------------------------------------------------------------------

# Create new contact
contact = {
    "Vorname": "Tina",
    "Name": "Test",
    "Strasse": "Teststreet 15",
    "PLZ": "0000",
    "Ort": "Testtown",
    "Land": {"LandNr": "CH"},
    "Anrede": "Mrs.",
    "EMail": "tina.test@example.org"}
response = proffix.request("POST", "ADR/ADRESSE", payload=contact)
adress_no = re.sub("^.*/", "", response.headers['Location'])

# Look up contact created above
response = proffix.request("GET", f"ADR/ADRESSE/{adress_no}")
response.json()["Vorname"]

# Display contacts matching a search string
response = proffix.request("GET", "ADR/ADRESSE", params={'Suche': 'Tina'})
address_list = response.json()
pd.DataFrame(address_list)

# Delete contact created above
response = proffix.request("DELETE", f"ADR/ADRESSE/{adress_no}")


# Logout -----------------------------------------------------------------------

# Terminate session to free license
proffix.logout()
```

## Run in Docker Container

```bash
docker pull python:latest
docker run -it --rm python:latest bash

pip install pandas
pip install https://github.com/lasuk/proffix_api/tarball/main
```


## Test Strategy

Unit tests in the python_api package are executed by gitlab after each commit,
when pull requests are created or modified, and once every day. Tests connect to
the public Proffix test environment.

## Package Development

- On Mac OS X, follow this
[post on stackoverflow](https://stackoverflow.com/questions/49470367/install-virtualenv-and-virtualenvwrapper-on-macos)
to install python and virtualenv with homebrew. Test with `which python` that
python points to the brew installation at `/usr/local/bin/python`.

- You probably want to work in a virtual environment for package development:

    ```bash
    mkvirtualenv env_name
    workon env_name
    ```

- To test the modified version of the package during development, clone the
package repository and invoke `python setup.py develop` in the repository root
folder. This merely adds a link to the package directory in the python search
path. When (re-)loading the package, the latest code version will be sourced.
