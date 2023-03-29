class Local(models.Model):                  # the class where your local data is saved
    _DATABASE = 'default'

    name = models.CharField(max_length=50)
    data = models.JSONField()
    
class Remote(models.Model):                 # the class for the remote data
    _DATABASE = 'remotedata'
    
    name = models.CharField(max_length=20)
    data = models.JSONField()




class CustomRouter(object):

    def db_for_read(self, model, **hints):
        return getattr(model, "_DATABASE", "default")

    def db_for_write(self, model, **hints):
        return getattr(model, "_DATABASE", "default")

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are
        in the master/slave pool.
        """
        db_list = ('default', 'remotedata')
        return obj1._state.db in db_list and obj2._state.db in db_list

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All non-auth models end up in this pool.
        """
        return True



DATABASES = {
    'default': {                                        # the default local db, in this case posgres as well in a docker
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }, 
    'remotedata' : {                                    # conveniently, postgres on supabase as well
        'ENGINE' : 'django.db.backends.postgresql',
        'NAME' : 'postgres',
        'HOST' : os.environ.get('SUPABASE_HOST'),
        'PASSWORD': os.environ.get('SUPABASE_PW'),
        'PORT': 5432,
        'USER': 'postgres',
        'CERT' : 'config.prod-ca-2021.crt',             # download this from database/settings and put in your main app folder
    }
}


DATABASE_ROUTERS = ['config.routers.CustomRouter']      # don't forget to set this variable so django knows where to find the router
