from django import forms
from django.forms.fields import CharField
from drugcombinator.models import Drug
from drugcombinator.fields import GroupedModelMultipleChoiceField


class CombinatorForm(forms.Form):

    drugs_field = GroupedModelMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={
            'searchable': "Rechercher dans cette liste"
        }),
        queryset=(Drug.objects
            .order_by_translated('name')
            .order_by('category__name')
        ),
        choices_groupby='category',
        label="Drogues à combiner"
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['drugs_field'].empty_label = "Sélectionnez des substances"


class SearchForm(forms.Form):

    name_field = CharField(
        widget=forms.TextInput(attrs={
            'class': 'autocomplete', # Materialize CSS class
            'autocomplete': 'off' # Disable defeult browser autocomplete
        }),
        label="Rechercher une substance",
        label_suffix=''
    )
