"""api_client

The api_client module implements the ProffixAPIClient class
that provides connectivity to the PROFFIX REST API.
"""
import hashlib
import json
import requests

class ProffixAPIError(IOError):
    """Error reported by the Proffix REST API."""

"""Interface to the PROFFIX REST API"""
class ProffixAPIClient():

    base_url = None
    username = None
    password_sha256 = None
    database = None
    modules = None
    _session_id = None

    @classmethod
    def _request_with_key_authentication(cls, api_key, endpoint, base_url):
        if base_url[-1] != "/":
            url = f"{base_url}/{endpoint}"
        else:
            url = f"{base_url}{endpoint}"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'}
        params = {
            "key": hashlib.sha256(api_key.encode('utf-8')).hexdigest()}
        response = requests.get(url, params=params, headers=headers)
        if not response.ok:
            msg = f"{response.json()['Type']}: {response.json()['Message']}"
            raise ProffixAPIError(msg, response)
        return response


    @classmethod
    def info(cls, api_key,
             base_url="https://remote.proffix.net:11011/pxapi/v4"):
        response = cls._request_with_key_authentication(
            api_key=api_key, endpoint="PRO/INFO", base_url=base_url)
        return response.json()


    @classmethod
    def database(cls, api_key,
                 base_url="https://remote.proffix.net:11011/pxapi/v4"):
        response = cls._request_with_key_authentication(
            api_key=api_key, endpoint="PRO/DATENBANK", base_url=base_url)
        return response.json()


    def __init__(self, username, password, database, modules=["VOL"],
                 base_url="https://remote.proffix.net:11011/pxapi/v4"):
        self.username = username
        self.password_sha256 = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.database = database
        self.modules = modules
        self.base_url = base_url
        if self.base_url[-1] != "/":
            self.base_url = self.base_url + "/"
        self._session_id = self.login()


    def login(self):
        url = f"{self.base_url}PRO/LOGIN"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'}
        data = {
            "Benutzer": self.username,
            "Passwort": self.password_sha256,
            "Datenbank": {"Name": self.database},
            "Module": self.modules}
        response = requests.post(url, json=data, headers=headers)
        if not response.ok:
            msg = f"{response.json()['Type']}: {response.json()['Message']}"
            raise ProffixAPIError(msg, response)
        return response.headers['PxSessionId']


    def logout(self):
        if self._session_id != None:
            self.request("DELETE", "PRO/LOGIN")
            self._session_id = None
        pass


    def request(self, method, endpoint, payload={}, params={}):
        if self._session_id == None:
            self._session_id = self.login()
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'PxSessionId': self._session_id}
        response = requests.request(method, url, json=payload,
                                    headers=headers, params=params)
        if (response.status_code == 401):
            # If response is 'Unauthorized', the session id might have expired.
            # Log out and back in to start a new session and try again.
            self.logout()
            self._session_id = self.login()
            headers['PxSessionId'] = self._session_id
            response = requests.request(method, url, json=payload,
                                        headers=headers, params=params)
        if not response.ok:
            err = response.json()
            msg = f"{err.pop('Type')}: {err.pop('Message')} {json.dumps(err)}"
            raise ProffixAPIError(msg, response)
        self._session_id = response.headers['PxSessionId']
        return response


    def file_upload(self, path, params):
        if self._session_id == None:
            self._session_id = self.login()
        url = f"{self.base_url}PRO/Datei"
        headers = {
            'Content-Type': 'application/octet-stream',
            'PxSessionId': self._session_id}
        data = open(path,'rb')
        response = requests.request("POST", url, data=data,
                                    headers=headers, params=params)
        if (response.status_code == 401):
            # If response is 'Unauthorized': log out, log back in and try again
            self.logout()
            self._session_id = self.login()
            response = requests.request("POST", url, data=data,
                                        headers=headers, params=params)
        if not response.ok:
            err = response.json()
            msg = f"{err.pop('Type')}: {err.pop('Message')} {json.dumps(err)}"
            raise ProffixAPIError(msg, response)
        self._session_id = response.headers['PxSessionId']
        return response
