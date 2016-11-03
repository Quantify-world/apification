from django.apps import AppConfig


class ApificationConfig(AppConfig):
    name = 'apification'

    def ready(self):
        import apification.checks
