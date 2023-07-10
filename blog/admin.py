from django.contrib import admin
from django.utils.translation import gettext as _
from modeltranslation.admin import TabbedTranslationAdmin

from blog.models import Article
from drugcombinator.admin import ChangedFieldsHistoryAdmin


class ArticleAdmin(ChangedFieldsHistoryAdmin):
    list_display = ('__str__', 'slug', 'author', 'created')
    date_hierarchy = 'last_modified'
    search_fields = ('title', 'slug', 'content')

    fieldsets = (
        (None, {
            'fields': (
                ('title', 'slug'),
                'content',
            )
        }),
        (_("Metadata"), {
            'fields': (
                'author',
                ('created', 'last_modified'),
            ),
        }),
    )
    readonly_fields = ('last_modified',)
    prepopulated_fields = {'slug': ('title',)}

    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)

        # Author field initial value has to match current user
        form.base_fields['author'].initial = request.user

        # Articles are not a good place to edit, add or remove users
        form.base_fields['author'].widget.can_delete_related = False
        form.base_fields['author'].widget.can_change_related = False
        form.base_fields['author'].widget.can_add_related = False

        return form


@admin.register(Article)
class TranslatedArticleAdmin(ArticleAdmin, TabbedTranslationAdmin):
    pass
