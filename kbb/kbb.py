import httplib2
import os
import configparser

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools




class Kbb(object):

    # If modifying these scopes, delete these previously saved credentials
    SCOPES = 'https://www.googleapis.com/auth/tasks'
    APPLICATION_NAME = 'KanBanBoard'


    def _get_credentials(self, kbb_dir):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        credential_dir = os.path.join(kbb_dir, 'credentials/')
        client_secret_file = os.path.join(kbb_dir, 'secrets/client_secret.json')

        # create directory if it doesn't exist yet
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)

        # extract credentials
        credential_path = os.path.join(credential_dir, 'kbb-credentials.json')
        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()

        # handle missing or invalid credentials
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(client_secret_file, Kbb.SCOPES)
            flow.user_agent = Kbb.APPLICATION_NAME
            credentials = tools.run_flow(flow, store, None)
            print('Storing credentials to ' + credential_path)

        return credentials


    def _load_config(self, kbb_dir, config):
        """Loads kbb configuration options
        
        Args:
            kbb_dir: root directory of kbb files
            config: dict to load configuration options into. For example:
                
                {'CapitalizedTopLevelConfig: 'True',
                 'lowercaseListConfig: [1,2,3,4]'}
                
        Returns:
            :type:`None`
        """
        config_file_path = os.path.join(kbb_dir, 'config')
        config_parser = configparser.ConfigParser()

        try:
            config_parser.read(config_file_path)
            general = config_parser['General']
            stages = config_parser['Stages']

            # first load general options
            config['SyncRate'] = general.getint('SyncRate', fallback=60)

            # load stage options
            config['stages'] = list()
            for key in stages:
                if stages.getboolean(key):
                    config['stages'].append(key)

        except ParsingError:
            print('Error parsing config file. Aborting.')
            raise ParsingError

        except NoSectionError:
            print('Required config section not found. Aborting.')
            raise NoSectionError

        return None


    def add_task(self, task, stage, task_id=None):
        """Adds a task object into the board.

        If task_id is not provided, one will be generated based on task contents.
        However, the caller must then use :func:`get_task_list` to find the task
        that it inserted into the board if the caller wants to later manipulate
        said task.

        Args:
            task: task of class :class:`Task` to be inserted into the board
            stage: the stage name (type string) for the task to be inserted
                into
            task_id: a unique identifier string for the task to be later
                identified by
        
        Returns:
            :type:`None`
        """
        return None


    def move_task(self, task_id, dest_stage):
        """Move a specified task into :param:`dest_stage`.

        Args:
            task_id: a unique identifier string for the specifc task
            dest_stage: the stage name (type string) for the task to be inserted
                into

        Returns:
            :type:`None`
        """
        pass


    def delete_task(self, task_id):
        """Deletes a specified task from the board.

        Args:
            task_id: a unique identifier string for the specifc task

        Returns:
            The deleted :class:`Task` object
        """
        pass


    def sync(self):
        """Syncs local database with Google cloud."""
        pass


    def get_task_list(self, stage=None, include_pending=True):
        """Return the list of all tasks in our board.

        Args:
            stage: Only tasks belonging to this stage will be returned
            include_pending: Whether or not to include tasks that haven't
                been synced to Google Tasks yet

        Returns:
            A list of :class:`Task` objects
        """
        pass


    def get_stage_names(self):
        """Returns a list of all stage names"""
        return None

    
    def __init__(self, kbb_dir=None):
        if not kbb_dir:
            home_dir = os.path.expanduser('~')
            kbb_dir = os.path.join(home_dir, '.kbb/')

        # GTasks API boilerplate
        credentials = self._get_credentials(kbb_dir)
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('tasks', 'v1', http=http)

        # setup config options
        self.config = dict()
        self._load_config(kbb_dir, self.config)


def main():
    """Shows basic usage of the Google Tasks API."""
    kbb_dir = os.path.join(os.path.expanduser('~'), '.kbb/')
    kbb = Kbb(kbb_dir)

    # execute query
    results = kbb.service.tasklists().list(maxResults=10).execute()

    # parse query results
    items = results.get('items', [])
    if not items:
        print('No task lists found.')
    else:
        print('Task lists:')
        for item in items:
            print('{0} ({1})'.format(item['title'], item['id']))

    # get some example tasks
    tasks = kbb.service.tasks().list(tasklist='@default').execute()
    while True:
        for task in tasks['items']:
            print(task['title'])
        print(len(tasks['items']))
        
        if 'nextPageToken' not in tasks:
            break

        tasks = kbb.service.tasks().list(tasklist='@default', 
                                     pageToken=tasks['nextPageToken']).execute()
    

if __name__ == '__main__':
    main()
