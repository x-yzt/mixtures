from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from drugportals.models import Portal


class PortalAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    date_hierarchy = 'last_modified'
    search_fields = ('name',)

    fields = (
        ('name', 'drug'),
    )


@admin.register(Portal)
class TranslatedPortalAdmin(PortalAdmin, TabbedTranslationAdmin):
    pass
