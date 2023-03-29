from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SbusersConfig(AppConfig):
    # default_auto_field = "django.db.models.BigAutoField"
    # name = "sbusers"

    name = "aininjas.sbusers"
    verbose_name = _("SbUsers")

    def ready(self):
        try:
            import aininjas.users.signals  # noqa F401
        except ImportError:
            pass

