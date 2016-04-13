import peewee

# This un-initialized database should be initialized before
# any instance Task is created
database = peewee.SqliteDatabase(None) 

class Action(peewee.Model):
    """Class representation of a single action
    
    Action is defined as any action the caller of the :class:`Kbb` has taken.
    Examples include:
        - Adding a task to the board
        - Removing a task from the board
        - Moving a task between stages
        - etc.
    """

    TASKADD = "taskadd"  # add a new task
    TASKDEL = "taskdel"  # delete a task
    TASKMOV = "taskmov"  # move a task between stages


    task_ident = peewee.TextField()
    task_action = peewee.CharField()
    start_stage = peewee.CharField()
    end_stage = peewee.CharField()


    class Meta:
        database = database # This model uses the "people.db" database.
