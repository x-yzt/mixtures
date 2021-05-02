from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from modeltranslation.admin import TabbedTranslationAdmin
from simple_history.admin import SimpleHistoryAdmin

from drugcombinator.models import Drug, Interaction, Category, Note

admin.site.site_header = "Mixtures.info"
admin.site.site_title = _("Mixtures.info adminisration")
admin.site.index_title = _("Welcome to Mixtures.info administration")
admin.site.enable_nav_sidebar = False


def set_draft_status(status:bool):
    def action(self, request, queryset):
        queryset.update(is_draft=status)
    return action


class ChangedFieldsHistoryAdmin(SimpleHistoryAdmin):
    """
        Modified SimpleHistoryAdmin that allows viewing changed fields
        in history list.
    """

    history_list_display = ('modified_fields',)

    def modified_fields(self, obj):
        fields = []
        prev = obj.prev_record
        if prev:
            fields = obj.diff_against(prev).changed_fields
        return ', '.join(fields) or _("No modification")


class CustomizableModelAdmin(admin.ModelAdmin):
    """
        ABC allowing to override model fields help_texts and labels.
        Adding help texts to computed or readonly admin fields is also
        supported.
        
        Admin classes inheriting this ABC simply needs to define two
        dicts named help_texts and labels.

        Exemple:
        help_texts = {'field_name': 'help_text_override'}
        labels = {'field_name': 'label_override'}
    """

    help_texts = {}
    labels = {}

    def get_form(self, *args, **kwargs):
        kwargs.update({'help_texts': self.help_texts})
        kwargs.update({'labels': self.labels})
        return super().get_form(*args, **kwargs)


class CustomizableInlineAdmin(admin.options.InlineModelAdmin):
    """
        This ABC works exactly like CustomizableModelAdmin, but allows
        inlines customizations.
    """

    help_texts = {}
    labels = {}

    def get_formset(self, *args, **kwargs):
        kwargs.update({'help_texts': self.help_texts})
        kwargs.update({'labels': self.labels})
        return super().get_formset(*args, **kwargs)


class InteractionInline(admin.StackedInline, CustomizableInlineAdmin):
    model = Interaction
    fk_name = 'from_drug'

    fieldsets = (
        (None, {
            'classes': ('vertical-label',),
            'fields': ((
                'from_drug', 'to_drug', 'risk', 'risk_reliability',
                'synergy', 'effects_reliability', 'is_draft'
            ),)
        }),
        (_("Descriptions"), {
            'classes': ('collapse',),
            'fields': (('risk_description', 'effect_description'),),
        }),
    )
    labels = {
        'from_drug': _("Other substance"),
        'to_drug': _("Other substance")
    }
    ordering = ('to_drug',)
    autocomplete_fields = ('to_drug',)
    classes = ('collapse',)
    extra = 0
    show_change_link = True
    verbose_name_plural = _("Interactions (second part)")


    class Media:
        css = {
            'all': ('mixtures/css/admin/forms.min.css',),
        }


# As Django currently (3.1.0) lacks decent symmetrical recursive M2M
# support, inlines generated by this class are prepended to the regular
# InteractionInlines in DrugAdmin.
class InteractionInlineFirst(InteractionInline):
    fk_name = 'to_drug'

    ordering = ('from_drug',)
    autocomplete_fields = ('from_drug',)
    verbose_name_plural = _("Interactions (first part)")


class DrugAdmin(ChangedFieldsHistoryAdmin):
    list_display = ('__str__', 'slug', 'aliases', 'common')
    list_filter = ('category', 'common')
    date_hierarchy = 'last_modified'
    search_fields = ('name', 'slug', '_aliases')

    fieldsets = (
        (None, {
            'fields': (
                ('name', 'slug'),
            )
        }),
        (_("Base informations"), {
            'fields': (
                ('common', 'category'),
                '_aliases'
            ),
        }),
        (_("Detailled informations"), {
            'fields': (
                (('description', 'related_notes'),)
            ),
        }),
        (_("Interaction data"), {
            'description': _(
                "Interaction data that does no depends on another "
                "specific substance. Those texts will be displayed in "
                "all interaction cards about this substance."
            ),
            'fields': (
                (('risks', 'effects'),)
            ),
        }),
    )
    readonly_fields = ('related_notes',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = (InteractionInlineFirst, InteractionInline)

    def related_notes(self, obj):
        data = {'drugs': (obj,)}
        return render_to_string('drugcombinator/admin/notes.html', data)
    related_notes.short_description = _("Related notes")

    def get_inline_instances(self, request, obj=None):
        # Hide inlines in popup windows. More info:
        # https://stackoverflow.com/a/56890626/7021223
        if '_to_field' in request.GET and '_popup' in request.GET:
            return []
        return super().get_inline_instances(request, obj=None)


@admin.register(Drug)
class TranslatedDrugAdmin(DrugAdmin, TabbedTranslationAdmin):
    pass


class InteractionAdmin(ChangedFieldsHistoryAdmin, CustomizableModelAdmin):
    list_display = ('__str__', 'is_draft', 'risk', 'synergy')
    list_filter = ('is_draft', 'risk', 'synergy')
    date_hierarchy = 'last_modified'
    search_fields = (
        'from_drug__name', 'from_drug___aliases',
        'to_drug__name', 'to_drug___aliases',
        'risk_description', 'effect_description'
    )
    actions = ('set_draft', 'set_published', 'reorder_interactants')

    history_list_display = (
        ChangedFieldsHistoryAdmin.history_list_display + ('is_draft',)
    )

    fieldsets = (
        (None, {
            'fields': (
                ('from_drug', 'to_drug', 'is_draft'),
            )
        }),
        (_("Interaction data"), {
            'fields': (
                ('risk', 'risk_reliability', 'drugs_risks'),
                ('risk_description',),
                ('synergy', 'effects_reliability', 'drugs_effects'),
                ('effect_description',),
            ),
            'classes': ('vertical-label',)
        }),
        (_("Notes"), {
            'fields': (
                ('notes', 'related_notes'),
            ),
        }),
    )
    help_texts = {
        'drugs_risks': _(
            "Those data will be automatically added to the \"risks\" "
            "field in the app."
        ),
        'drugs_effects': _(
            "Those data will be automatically added to the \"effects\" "
            "field in the app."
        )
    }
    autocomplete_fields = ('from_drug', 'to_drug')
    readonly_fields = ('drugs_risks', 'drugs_effects', 'related_notes')
    radio_fields = {
        'risk': admin.VERTICAL,
        'synergy': admin.VERTICAL,
        'risk_reliability': admin.VERTICAL,
        'effects_reliability': admin.VERTICAL
    }

    def drugs_risks(self, obj):
        return render_to_string(
            'drugcombinator/admin/drugs_interactions.html',
            {
                'drugs': obj.interactants,
                'data_type': 'risks'
            }
        )
    drugs_risks.short_description = _("Substance-related risks")

    def drugs_effects(self, obj):
        return render_to_string(
            'drugcombinator/admin/drugs_interactions.html',
            {
                'drugs': obj.interactants,
                'data_type': 'effects'
            }
        )
    drugs_effects.short_description = _("Substance-related effects")

    def related_notes(self, obj):
        return render_to_string(
            'drugcombinator/admin/notes.html',
            {'drugs': obj.interactants}
        )
    related_notes.short_description = _("Related notes")
    
    set_draft = set_draft_status(True)
    set_draft.short_description = _(
        "Mark all selected interactions as drafts"
    )

    set_published = set_draft_status(False)
    set_published.short_description = _(
        "Mark all selected interactions as published"
    )

    def reorder_interactants(self, request, queryset):
        for interaction in queryset:
            interaction.save()
    reorder_interactants.short_description = _(
        "Sort the linked substances of selected interactions"
    )


    class Media:
        css = {
            'all': ('mixtures/css/admin/forms.min.css',),
        }


@admin.register(Interaction)
class TranslatedInteractionAdmin(InteractionAdmin, TabbedTranslationAdmin):
    pass


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug')
    date_hierarchy = 'last_modified'
    search_fields = ('name', 'slug', 'description')

    fields = (
        ('name', 'slug'),
        'description'
    )
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class TranslatedCategoryAdmin(CategoryAdmin, TabbedTranslationAdmin):
    pass


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    list_filter = ('related_drugs',)
    date_hierarchy = 'last_modified'
    search_fields = ('title', 'content')

    fields = (
        ('title', 'related_drugs'),
        'content'
    )
    autocomplete_fields = ('related_drugs',)
