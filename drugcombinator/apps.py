from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DrugcombinatorConfig(AppConfig):
    name = 'drugcombinator'
    verbose_name = _("Drug combinator")

    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        import drugcombinator.signals  # noqa: F401
