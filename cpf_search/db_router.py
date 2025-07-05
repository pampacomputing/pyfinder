class CnpjRouter:
    """A router to control all database operations on models in the
    cnpj_db database."""
    def db_for_read(self, model, **hints):
        """Attempts to read cnpj_db models go to cnpj_db."""
        if model._meta.app_label == 'cpf_search' and model._meta.db_table in ['empresas', 'socios']:
            return 'cnpj_db'
        return None

    def db_for_write(self, model, **hints):
        """Attempts to write cnpj_db models go to cnpj_db."""
        if model._meta.app_label == 'cpf_search' and model._meta.db_table in ['empresas', 'socios']:
            return 'cnpj_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if a model in the cnpj_db app is involved."""
        if obj1._meta.app_label == 'cpf_search' and obj1._meta.db_table in ['empresas', 'socios'] or \
           obj2._meta.app_label == 'cpf_search' and obj2._meta.db_table in ['empresas', 'socios']:
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Make sure the cnpj_db app only appears in the 'cnpj_db'
        database."""
        if app_label == 'cpf_search' and model_name in ['empresas', 'socios']:
            return db == 'cnpj_db'
        return None

