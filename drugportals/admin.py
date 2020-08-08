from django.contrib import admin
from drugportals.models import Portal


@admin.register(Portal)
class PortalAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    date_hierarchy = 'last_modified'
    search_fields = ('name',)

    fields = (
        ('name', 'drug'),
    )
