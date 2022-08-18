from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DrugportalsConfig(AppConfig):
    name = 'drugportals'
    verbose_name = _("Drug portals")

    default_auto_field = 'django.db.models.AutoField'
