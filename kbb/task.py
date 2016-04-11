import peewee

# This un-initialized database should be initialized before
# any instance Task is created
database = peewee.SqliteDatabase(None) 

class Task(peewee.Model):
    """Class representation of a single task"""

    # public properties
    title = peewee.TextField()
    stage = peewee.CharField()
    due = peewee.DateField()
    notes = peewee.TextField()
    status = peewee.CharField()
    ident = peewee.TextField()


    class Meta:
        database = database # This model uses the "people.db" database.
