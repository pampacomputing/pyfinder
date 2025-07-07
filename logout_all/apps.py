from django.apps import AppConfig

class LogoutAllConfig(AppConfig):
    name = 'logout_all'

    def ready(self):
        from django.contrib.sessions.models import Session
        # This will run when the app is ready
        # We will clear all sessions here
        Session.objects.all().delete()
        print("All sessions cleared on server startup.")