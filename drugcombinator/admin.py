from django.contrib import admin
from drugcombinator.models import Drug, Interaction, Category


admin.site.site_header = "Mixtures.info"
admin.site.site_title = "Administration de Mixtures.info"
admin.site.index_title = "Bienvenue dans l'administration de Mixtures.info"


class InteractionInline(admin.StackedInline):
    model = Interaction
    fk_name = 'from_drug'

    fieldsets = (
        (None, {
            'fields': (('to_drug', 'risk', 'pharmaco'),)
        }),
        ('Descriptions', {
            'classes': ('collapse',),
            'fields': (('risk_description', 'effect_description'),),
        }),
    )
    autocomplete_fields = ('to_drug',)


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug', 'aliases', 'common')
    list_filter = ('category', 'common')
    date_hierarchy = 'added'
    search_fields = ('name', 'slug', '_aliases')

    fieldsets = (
        (None, {
            'fields': (
                ('name', 'slug'),
            )
        }),
        ("Informations de base", {
            'fields': (
                ('common', 'category'),
                '_aliases'
            ),
        }),
        ("Informations détaillées", {
            'fields': (
                ('description',)
            ),
        }),
    )
    prepopulated_fields = {'slug': ('name',)}
    inlines = (InteractionInline,)


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'risk', 'pharmaco')
    list_filter = (
        'from_drug', 'to_drug',
        'risk', 'pharmaco'
    )
    date_hierarchy = 'added'
    search_fields = (
        'from_drug', 'to_drug',
        'risk_description', 'effect_description'
    )

    fields = (
        ('from_drug', 'to_drug'),
        ('risk', 'risk_description'),
        ('pharmaco', 'effect_description')
    )
    autocomplete_fields = ('from_drug', 'to_drug')
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
