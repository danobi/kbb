import httplib2
import os
import configparser
import uuid
import time
import binascii
from datetime import datetime

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import peewee

import kbb.task as task
from  kbb.task import Task as Task
import kbb.action as action
from kbb.action import Action as Action


class Kbb(object):

    # If modifying these scopes, delete these previously saved credentials
    SCOPES = 'https://www.googleapis.com/auth/tasks'
    APPLICATION_NAME = 'KanBanBoard'
    DEFAULT_TASK_LIST = '@default'

    
    def _convert_str_to_iso3339(self, timestamp):
        """Convert an ISO-3339 string to datetime

        Args:
            timestamp: string representation of ISO-3339 time
        
        Returns:
            :class:`datetime` object

        Example:
            >>> ts = time.strptime('1985-04-12T23:20:50.52Z', '%Y-%m-%dT%H:%M:%S.%fZ')
            >>> ts
            time.struct_time(tm_year=1985, tm_mon=4, tm_mday=12, tm_hour=23, tm_min=20, ....
        """
        dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
        return dt


    def _generate_uuid(self, length):
        """Generate a random UUID

        Note: this function may generate collisions... but we're banking
        on the fact that it is statistically very, very unlikely

        Args:
            length: Length of the UUID to be generated

        Returns:
            :type:`str` UUID
        """
        random_data = os.urandom(length)
        string_representation = binascii.b2a_hex(random_data).decode()
        uuid = string_representation[:length]
        return uuid


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
                    config['stages'].append(key.lower())

        except ParsingError:
            print('Error parsing config file. Aborting.')
            raise ParsingError

        except NoSectionError:
            print('Required config section not found. Aborting.')
            raise NoSectionError

        return None


    def _locate_task(self, task_id):
        """Find a task by its task_id"""
        result_tasks = Task.select().where(Task.task_id == task_id)

        if not result_tasks:
            raise Exception('task_id not found')

        elif len(result_tasks) > 1:
            raise Exception('task_id is not unique')

        return result_tasks[0]


    def _insert_task_to_gtasks(self, task_id):
        """Inserts the given task into the cloud

        Note: this task should not already be present in the cloud.
        
        Args:
            task_id: ID of the task to be inserted
        """
        new_task = self._locate_task(task_id)
        new_task_dict = Task.to_gtask_dict(new_task)
        result = self.service.tasks().insert(tasklist=self.DEFAULT_TASK_LIST, 
                                             body=new_task_dict).execute()


    def _delete_task_from_gtasks(self, task_id):
        """Deletes the given task from the cloud.

        Args:
            task_id: ID of the task to be deleted
        """
        self.service.tasks().delete(tasklist=self.DEFAULT_TASK_LIST, 
                                    task=task_id).execute()


    def _update_task_to_done(self, task_id):
        """Updates the given task to done in the cloud.

        Args:
            task_id: ID of the task to be marked as done
        """
        # grab & update the existing task from the cloud
        updated_task = self.service.tasks().get(tasklist=self.DEFAULT_TASK_LIST, 
                                                task=task_id).execute()
        updated_task['status'] = Task.DONE

        # push the updated task back into the cloud
        result = self.service.tasks().update(tasklist=self.DEFAULT_TASK_LIST, 
                                             task=updated_task['id'], 
                                             body=updated_task).execute()


    def _update_task_to_notdone(self, task_id):
        """Updates the given task to not done in the cloud.

        Args:
            task_id: ID of the task to be marked as not done
        """
        # grab the existing task from the cloud
        updated_task = self.service.tasks().get(tasklist=self.DEFAULT_TASK_LIST, 
                                                task=task_id).execute()
        # task on disk
        task = self._locate_task(task_id)

        if updated_task['status'] == Task.DONE:
            updated_task['status'] = Task.NOTDONE

            # delete the old task and insert new task
            # Note: for whatever reason using the update() function doesn't work,
            #       so we're left with this option
            self.service.tasks().delete(tasklist=self.DEFAULT_TASK_LIST,
                                        task=task.task_id).execute()
            task_dict = Task.to_gtask_dict(task)
            result = self.service.tasks().insert(tasklist=self.DEFAULT_TASK_LIST, 
                                                 body=task_dict).execute()


    def _get_all_task_ids_in_db(self):
        """Retrieve all task UUIDs in local database
        
        Returns:
            :type:`set` of all task UUIDs in local database
        """
        id_set = set()
        task_list = Task.select()

        for t in task_list:
            if t.task_id in id_set:
                raise Exception('task UUID collision')

            id_set.add(t.task_id)

        return id_set


    def _get_all_cloud_tasks(self):
        """Gets a list of all tasks present in the cloud

        Returns:
            :type:`list` of task dictionaries
        """
        list_of_tasks = list()
        tasks = self.service.tasks().list(tasklist=self.DEFAULT_TASK_LIST).execute()

        while True:
            [list_of_tasks.append(t) for t in tasks['items']]
            
            if 'nextPageToken' not in tasks:
                break

            tasks = self.service.tasks().list(tasklist=self.DEFAULT_TASK_LIST,
                                             pageToken=tasks['nextPageToken']).execute()

        return list_of_tasks



    def _sync_local_to_cloud(self):
        """Sync local changes to the GTasks cloud"""
        # grab all actions that need to be performed
        action_list = Action.select()

        for act in action_list:
            if act.task_action == Action.TASKADD:
                self._insert_task_to_gtasks(act.task_ident)

            elif act.task_action == Action.TASKDEL:
                self._delete_task_from_gtasks(act.task_ident)

            elif act.task_action == Action.TASKMOV:
                # we only mark the task as completed in GTasks if the 
                # destination stage is the final (right most) stage
                if act.end_stage == self.get_stage_names()[-1]:
                    self._update_task_to_done(act.task_ident)

                # else we mark the task as not completed 
                else:
                    self._update_task_to_notdone(act.task_ident)

            # remove row from database since we don't want to run this action
            # again on the next sync
            act.delete_instance()


    def _sync_cloud_to_local(self):
        """Pull in any cloud changes to local database"""
        cloud_task_list = self._get_all_cloud_tasks()
        local_task_list = self.get_task_list()
        local_uuid_set = self._get_all_task_ids_in_db()

        # first look at any differences between the set(cloud) - set(local)
        for t in cloud_task_list:
            # add into local database any tasks not already present
            if t['id'] not in local_uuid_set:
                t_notes = t['notes'] if 'notes' in t else ""

                if 'due' in t:
                    t_due = self._convert_str_to_iso3339(t['due']) 
                else:
                    t_due = datetime.today()
                    t_due = t_due.replace(hour=0, minute=0, second=0, microsecond=0)

                if t['status'] == Task.DONE:
                    t_stage = self.get_stage_names()[-1] 
                else: 
                    t_stage = self.get_stage_names()[0]

                self._new_task(t['title'],
                              stage=t_stage,
                              due=t_due,
                              notes=t_notes,
                              status=t['status'],
                              task_id=t['id'],
                              cloud_sync=False)

            # if the task is set to DONE in the cloud and NOTDONE locally,
            # it must mean that the task was changed in the cloud side, 
            # since all stage changes made locally are queued up in the 
            # Action table
            elif t['id'] in local_uuid_set:
                local_task = self._locate_task(t['id'])
                if t['status'] != local_task.status:
                    local_task.status = t['status']
                    local_task.save()

        # next look at a ny differences between set(local) - set(cloud)
        for t in local_task_list:
            # if we have a local copy, our Action table is empty, and the cloud
            # doesn't possess a copy, we delete the local copy
            found = False
            for cloud_t in cloud_task_list:
                if t.task_id == cloud_t['id']:
                    found = True

            action_queue = Action.select()
            if not found and not len(action_queue):
                t.delete_instance()




    def _new_task(self, title, stage, due, notes, status, task_id, cloud_sync):
        """Internal new task creator

        Args:
            title: Title of the task 
            stage: the stage name (type string) for the task to be inserted into 
            due: :class:`Datetime.datetime` object of when the task is due
            notes: Additional notes related to the task
            status: Status of task. Either DONE or NOTDONE
            task_id: GTasks compatible task id (42 character alphanum string)
            cloud_sync: whether or not to sync this new task with GTasks cloud
        
        Returns:
            The added :class:`Task`
        """
        t = Task.create(title=title,
                        stage=stage,
                        due=due, 
                        notes=notes,
                        status=status,
                        task_id=task_id,
                        deleted=False)
        t.save()

        # create Action to be later updated to the cloud
        if cloud_sync:
            Action.create(task_ident=task_id,
                          task_action=Action.TASKADD,
                          start_stage='None',
                          end_stage=stage).save()
            self.sync()

        return t



    def new_task(self, 
                 title, 
                 stage=None,
                 due=None,
                 notes=None,
                 status=None,
                 cloud_sync=True):
        """Adds a task object into the board.

        This is essentially a factory class for Task objects. It is
        needed because of how unintuitive creating peewee objects are.

        The returned object could be either be further manipulated or 
        stored by the caller.

        The caller must then use :func:`get_task_list` to find the task
        that it inserted into the board if the caller wants to later manipulate
        said task.

        Args:
            title: Title of the task 
            stage: the stage name (type string) for the task to be inserted into (optional)
            due: :class:`Datetime.datetime` object of when the task is due (optional)
            notes: Additional notes related to the task (optional)
            status: Status of task. Either DONE or NOTDONE (optional)
        
        Returns:
            The added :class:`Task`
        """
        if not title:
            raise ValueError('no task title')

        if not stage:
            stage = self.get_stage_names()[0]
        elif stage.lower() not in self.get_stage_names():
            raise KeyError('{0} not in list of stages'.format(stage))

        if not due:
            # default time is for a task to be due today (year, month, and date specifiers only)
            due = datetime.today()
            due = due.replace(hour=0, minute=0, second=0, microsecond=0)

        if not notes:
            notes = ""

        if not status:
            status = Task.NOTDONE

        task_id = self._generate_uuid(Task.UUID_LENGTH)

        return self._new_task(title, stage, due, notes, status, task_id, cloud_sync)


    def move_task(self, task_id, dest_stage):
        """Move a specified task into :param:`dest_stage`.

        Args:
            task_id: a unique identifier string for the specifc task
            dest_stage: the stage name (type string) for the task to be inserted
                into

        Returns:
            :type:`None`
        """
        t = self._locate_task(task_id)
        old_stage = t.stage
        t.stage = dest_stage
        if dest_stage != self.get_stage_names()[-1]:
            t.status = Task.NOTDONE
        t.save()

        # create Action to be later updated to the cloud
        Action.create(task_ident=task_id,
                      task_action=Action.TASKMOV,
                      start_stage=old_stage,
                      end_stage=dest_stage).save()

        self.sync()


    def delete_task(self, task_id):
        """Deletes a specified task from the board.

        Args:
            task_id: a unique identifier string for the specifc task

        Returns:
            The deleted :class:`Task` object
        """
        t = self._locate_task(task_id)
        t.deleted = True
        t.save()

        # create Action to be later updated to the cloud
        Action.create(task_ident=task_id,
                      task_action=Action.TASKDEL,
                      start_stage=t.stage,
                      end_stage='None').save()

        self.sync()


    def sync(self):
        """Syncs local database with Google cloud.

        This function will first pull in any updates from the GTasks
        cloud.
        
        Then this function will look inside the :class:`Action` table to
        see what actions need to still be syned with the cloud.

        In the case that we are offline, we will do nothing and simply 
        wait for the next invocation of this function.
        
        TODO: handle offline case
        """
        self._sync_local_to_cloud()
        self._sync_cloud_to_local()


    def get_task_list(self, stage=None, include_pending=True):
        """Return the list of all tasks in our board.

        Note: include_pending isn't implemented in this release version
        yet since it's usefulness is doubtful to me

        Args:
            stage: Only tasks belonging to this stage will be returned
            include_pending: Whether or not to include tasks that haven't
                been synced to Google Tasks yet

        Returns:
            A list of :class:`Task` objects
        """
        if not stage:
            return list(Task.select())

        elif stage and stage.lower() in self.get_stage_names():
            return list(Task.select().where(Task.stage == stage))

        else:
            raise KeyError('{0} not in list of stages'.format(stage))


    def get_stage_names(self):
        """Returns a list of all stage names"""
        return list(self.config['stages'])

    
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

        # setup the Task class' database
        database_name = os.path.join(kbb_dir, 'kbbdb.db')
        task.database.init(database_name)
        if 'task' not in task.database.get_tables():
            task.database.create_tables([Task])

        # setup the Action class' database
        action.database.init(database_name)
        if 'action' not in action.database.get_tables():
            action.database.create_tables([action.Action])

        # now check to see we can access the database
        task.database.connect()
        task.database.close()
