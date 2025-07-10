class AppRouter:
    """
    A router to control all database operations for specific apps.
    """
    route_app_labels = {'cpf_search', 'cnpj_search'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'cpf_search':
            return 'basecpf_db'
        if model._meta.app_label == 'cnpj_search':
            return 'cnpj_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return None  # Prevent writes to read-only databases
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label in self.route_app_labels or \
           obj2._meta.app_label in self.route_app_labels:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'cpf_search':
            return db == 'basecpf_db'
        if app_label == 'cnpj_search':
            return db == 'cnpj_db'
        return db == 'default'