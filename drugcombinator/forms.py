from django import forms
from django.forms.fields import CharField
from django.utils.translation import gettext_lazy as _
from drugcombinator.models import Drug
from drugcombinator.fields import GroupedModelMultipleChoiceField


class CombinatorForm(forms.Form):

    drugs_field = GroupedModelMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={
            'searchable': _("Search in this list")
        }),
        queryset=(Drug.objects
            .order_by_translated('name')
            .order_by('category__name')
        ),
        choices_groupby='category',
        label=_("Substances to combine")
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['drugs_field'].empty_label = _("Select substances")


class SearchForm(forms.Form):

    name_field = CharField(
        widget=forms.TextInput(attrs={
            'class': 'autocomplete', # Materialize CSS class
            'autocomplete': 'off' # Disable defeult browser autocomplete
        }),
        label=_("Find a substance"),
        label_suffix=''
    )
