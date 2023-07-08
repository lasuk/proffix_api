import re, filecmp
from pkg_resources import resource_filename
from proffix_api import ProffixAPIClient

# Credetials for official Proffix API test environment are
# publicly available at
# https://www.proffix.ch/Portals/0/content/REST%20API/zugriff_auf_testumgebung.html
# We're not giving away a secret by including them in plain text.

def test_database_request():
    database = ProffixAPIClient.database(
        base_url = "https://remote.proffix.net:11011/pxapi/v4",
        api_key = "Demo_2016_PWREST!,Wangs")
    assert database[0]['Name'] == "DEMODB"
    pass

def test_info_request():
    version_info = ProffixAPIClient.info(
        base_url = "https://remote.proffix.net:11011/pxapi/v4",
        api_key = "Demo_2016_PWREST!,Wangs")
    assert version_info['Version'][0] == "4"
    assert version_info['NeuesteVersion'][0] == "4"
    pass

def test_api_login():
    proffix = ProffixAPIClient(
        base_url="https://remote.proffix.net:11011/pxapi/v4",
        username="Gast",
        password="gast123",
        database="DEMODB",
        modules=["VOL"])

    response = proffix.request("GET", "PRO/LOGIN")
    assert response.json()['Benutzer'] == "GAST"

    proffix.logout()
    pass

def test_file_handling():
    proffix = ProffixAPIClient(
        base_url="https://remote.proffix.net:11011/pxapi/v4",
        username="Gast",
        password="gast123",
        database="DEMODB",
        modules=["VOL"])

    # File upload
    test_file = resource_filename('proffix_api', 'resources/test_image.jpg')
    response = proffix.file_upload(
        path = test_file,
        params = {'filename': "test_image.jpg"})
    file_id = re.sub("^.*/", "", response.headers['Location'])

    # File info
    response = proffix.request("GET", f"PRO/Datei/{file_id}/Info")
    file_info = response.json()
    assert re.match(r"^.*/test_image.jpg.*$", file_info['Dateipfad'])

    # File download
    response = proffix.request("GET", f"PRO/Datei/{file_id}")
    open('test_image.jpg', 'wb').write(response.content)
    # Ensure original and downloaded files are identical
    assert filecmp.cmp('test_image.jpg', test_file)

    proffix.logout()
    pass
