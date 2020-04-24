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
            'fields': (('to_drug', 'risk', 'synergy'),)
        }),
        ('Descriptions', {
            'classes': ('collapse',),
            'fields': (('risk_description', 'effect_description'),),
        }),
    )
    autocomplete_fields = ('to_drug',)
    show_change_link = True


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

    def get_inline_instances(self, request, obj=None):
        # Hide inlines in popup windows. More info:
        # https://stackoverflow.com/a/56890626/7021223
        if '_to_field' in request.GET and '_popup' in request.GET:
            return []
        return super().get_inline_instances(request, obj=None)


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'risk', 'synergy')
    list_filter = (
        'from_drug', 'to_drug',
        'risk', 'synergy'
    )
    date_hierarchy = 'added'
    search_fields = (
        'from_drug__name', 'from_drug___aliases',
        'risk_description', 'effect_description'
    )

    fields = (
        ('from_drug', 'to_drug'),
        ('risk', 'risk_description'),
        ('synergy', 'effect_description'),
        'notes'
    )
    autocomplete_fields = ('from_drug', 'to_drug')
    radio_fields = {
        'risk': admin.VERTICAL,
        'synergy': admin.VERTICAL
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
