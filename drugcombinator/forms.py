from django import forms
from django.forms.fields import CharField
from django.utils.translation import gettext_lazy as _

from drugcombinator.models import Drug, Interaction
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
            'autocomplete': 'off' # Disable default browser autocomplete
        }),
        label=_("Find a substance"),
        label_suffix=''
    )


class ContribForm(forms.Form):
    
    message_field = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'materialize-textarea validate'
        }),
        label=_("Your contribution"),
        label_suffix='',
        help_text=_("Any remark or suggestion you might have about "
            "this data. Don't be shy ;)")
    )
    email_field = forms.EmailField(
        widget=forms.TextInput(attrs={
            'type': 'email',
            'class': 'validate'
        }),
        label=_("Your email address"),
        label_suffix='',
        help_text=_("We might need to contact you back about this "
            "contribution. We will not use your email for another "
            "purpose.")
    )
    interaction_field = forms.ModelChoiceField(
        queryset=Interaction.objects.all(),
        widget=forms.HiddenInput()
    )
