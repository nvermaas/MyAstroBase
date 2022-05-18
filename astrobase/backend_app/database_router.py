# this database routers only handles the traffic to the default app
# traffic to other apps is handled in the database_router in the other apps (like starcharts_app)
class DefaultRouter:

    apps_using_default_database = {'backend_app', 'exoplanets', 'transients_app', 'auth', 'authtoken','contenttypes', 'sessions', 'admin'}
    apps_using_stars_database = {'starcharts_app'}

    def db_for_read(self, model, **hints):
        
        if model._meta.app_label in self.apps_using_default_database:
            return 'default'
        #else:
        #    return 'stars'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.apps_using_default_database:
            return 'default'
        #else:
        #    return 'stars'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the query apps is
        involved.
        """
        if (
            obj1._meta.app_label in self.apps_using_default_database or
            obj2._meta.app_label in self.apps_using_default_database
        ):
           return True
        return None


    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the query apps only appear in the
        'query' database.
        """
        if app_label in self.apps_using_default_database:
            return db == 'default'
        #elif app_label in self.apps_using_stars_database:
        #    return db == 'stars'

        return None

