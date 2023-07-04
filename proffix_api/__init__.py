"""proffix_api package

**proffix_api** is a lightweight Python package to manage connections to the
REST API of Proffix, an ERP software popular in Switzerland. This package
simplifies the interaction with Proffix's API by automatically handling
authentication. It is designed as a thin wrapper that routes requests via
universal `get()`, `post()`, etc. methods and does not implement individual
endpoints.
"""

from proffix_api.api_client import ProffixAPIClient
from proffix_api.api_client import ProffixAPIError
