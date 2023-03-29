class AuthRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """
    route_app_labels = {'auth'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'auth_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'auth_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        print("#DEBUG cross db migrating db, app_label, model_name",db, app_label, model_name )
        if app_label in self.route_app_labels:
            return db == 'auth_db'
        return None



from django.conf import settings


class AuthDbRouter:
    """Oracle db2 schema rules for legacy DB.
    Avoid read/write/migrate for apps using db2 schema unless we are also
    trying to use the 'db2' DB as defined in settings.
    When we leave a method out or return "None" we are allowing the default
    routing to take over as defined in django.db.utils.ConnectionRouter.
    More: https://docs.djangoproject.com/en/3.0/topics/db/multi-db/
    """

    def _db_for_action(self, model, **hints):
        """Route to our database if one of our apps."""

        if model._meta.app_label in settings.ORACLE_DB2_ROUTER_APP_LABELS:
            return settings.ORACLE_DB2_ROUTER_DATABASE_NAME

        return None

    db_for_read = _db_for_action
    db_for_write = _db_for_action

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Only allow migration for our apps in the db2 db/schema.
        This will only pass with "--database=db2" on your migration
        command(s) on the CLI.
        """

        # If in our DB/schema, only migrate our apps (block django_* bits)
        if db == settings.ORACLE_DB2_ROUTER_DATABASE_NAME:
            return app_label in settings.ORACLE_DB2_ROUTER_APP_LABELS

        # If one of our apps, only migrate within our DB/schema
        if app_label in settings.ORACLE_DB2_ROUTER_APP_LABELS:
            return db == settings.ORACLE_DB2_ROUTER_DATABASE_NAME

        return None

    def allow_relation(self, obj1, obj2, **hints):
        db_set = {
            settings.ORACLE_DB2_ROUTER_DATABASE_NAME,
            *settings.ORACLE_DB2_ROUTER_ALLOWED_RELATIONS,
        }

        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True

        return None
