import peewee

# This un-initialized database should be initialized before
# any instance Task is created
database = peewee.SqliteDatabase(None) 

class Task(peewee.Model):
    """Class representation of a single task"""

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
