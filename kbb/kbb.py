import httplib2
import os
import argparse

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools


# If modifying these scopes, delete these previously saved credentials
SCOPES = 'https://www.googleapis.com/auth/tasks.readonly'
CLIENT_SECRET_FILE = os.path.join(os.path.expanduser('~'), '.kbb/secrets/client_secret.json')
APPLICATION_NAME = 'KanBanBoard'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.kbb/credentials')

    # create directory if it doesn't exist yet
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    # extract credentials
    credential_path = os.path.join(credential_dir, 'kbb-credentials.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()

    # handle missing or invalid credentials
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)

    return credentials


def main():
    """Shows basic usage of the Google Tasks API.

    Creates a Google Tasks API service object and outputs the first 10
    task lists.
    """
    # parse command line args if there is any
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

    # set up boilerplate
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('tasks', 'v1', http=http)

    # execute query
    results = service.tasklists().list(maxResults=10).execute()

    # parse query results
    items = results.get('items', [])
    if not items:
        print('No task lists found.')
    else:
        print('Task lists:')
        for item in items:
            print('{0} ({1})'.format(item['title'], item['id']))


if __name__ == '__main__':
    main()
