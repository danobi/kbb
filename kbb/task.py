import peewee

# This un-initialized database should be initialized before
# any instance Task is created
database = peewee.SqliteDatabase(None) 

class Task(peewee.Model):
    """Class representation of a single task
    
    Note: read this carefully:
        task_id's that are generated locally are *NOT* passed up to the cloud.
        The reason is that the GTasks API apparently doesn't take ids in the input
        for new tasks. 

        What actually happens in kbb is that when a new task is created locally, the
        local task gets put into the local database, then the local task is synced up
        to the cloud. The cloud then generates a new id. When we sync the cloud back to 
        the local database, the local task gets deleted and a new local task is created
        with the data from the cloud.

        So essentially, any task_id reference before a cloud sync does not point to 
        anything.
    """

    UUID_LENGTH = 44
    NOTDONE = "needsAction"
    DONE = "completed"


    # public properties
    title = peewee.TextField()
    stage = peewee.CharField()
    due = peewee.DateTimeField()
    notes = peewee.TextField()
    status = peewee.CharField()
    task_id = peewee.TextField()
    deleted = peewee.BooleanField()


    @staticmethod
    def to_gtask_dict(task):
        d = dict()

        # first the required fields
        d['title'] = task.title
        d['due'] = task.due.isoformat() + str('Z') # the Z is required by the GTasks API
        d['status'] = task.status
        #d['id'] = task.task_id

        # then the optional fields
        if task.notes:
            d['notes'] = task.notes

        return d


    class Meta:
        database = database # This model uses the "people.db" database.
