from django.contrib import admin
from drugcombinator.models import Drug, Interaction, Category


admin.site.site_header = "Mixtures.info"
admin.site.site_title = "Administration de Mixtures.info"
admin.site.index_title = "Bienvenue dans l'administration de Mixtures.info"


class InteractionInline(admin.StackedInline):
    model = Interaction
    fk_name = 'from_substance'

    fieldsets = (
        (None, {
            'fields': (('to_substance', 'risk', 'pharmaco'),)
        }),
        ('Descriptions', {
            'classes': ('collapse',),
            'fields': (('risk_description', 'effect_description'),),
        }),
    )
    autocomplete_fields = ('to_substance',)


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug', 'aliases')
    list_filter = ('category',)
    date_hierarchy = 'added'
    search_fields = ('name', 'slug', '_aliases')

    fields = (
        ('name', 'slug', 'category'),
        '_aliases',
        'description'
    )
    prepopulated_fields = {'slug': ('name',)}
    inlines = (InteractionInline,)


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'risk', 'pharmaco')
    list_filter = (
        'from_substance', 'to_substance',
        'risk', 'pharmaco'
    )
    date_hierarchy = 'added'
    search_fields = (
        'from_substance', 'to_substance',
        'risk_description', 'effect_description'
    )

    fields = (
        ('from_substance', 'to_substance'),
        ('risk', 'risk_description'),
        ('pharmaco', 'effect_description')
    )
    autocomplete_fields = ('from_substance', 'to_substance')
    radio_fields = {
        'risk': admin.VERTICAL,
        'pharmaco': admin.VERTICAL
    }

    def delete_queryset(self, request, queryset):
        # Tweak to call model delete() when using bulk deletion
        for obj in queryset:
            obj.delete()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug')
    date_hierarchy = 'added'
    search_fields = ('name', 'slug', 'description')

    fields = (
        ('name', 'slug'),
        'description'
    )
    prepopulated_fields = {'slug': ('name',)}
