from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from django.conf import settings

from lino.api import dd

try:
    import argparse

    tools_argparser = tools.argparser
    tools_argparser.add_argument('runserver', action="store")
    # flags = argparse.ArgumentParser(parents=[tools_argparser]).parse_args()
    # flags.add_argument('runserver', action="store", dest="runserver")
    # flags = flags.parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/people.googleapis.com-python-quickstart.json
SCOPES = getattr(settings.SITE, 'googleapi_people_scopes', dd.plugins['googleapi_people'].googleapi_people_scopes)
CLIENT_SECRET_FILE = getattr(settings.SITE, 'path_googleapi_client_secret_file',
                             dd.plugins['googleapi_people'].path_googleapi_client_secret_file)
APPLICATION_NAME = getattr(settings.SITE, 'googleapi_application_name',
                           dd.plugins['googleapi_people'].googleapi_application_name)


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials',settings.SITE.verbose_name)
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'people.googleapis.com-python-quickstart.json')
    # credential_path = CLIENT_SECRET_FILE

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        # flags = argparse.ArgumentParser(description='This is a PyMOTW sample program').parse_args()
        if flags:
            credentials = tools.run_flow(flow, store,flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('people', 'v1', http=http)
