from django import forms
from drugcombinator.models import Drug
from drugcombinator.fields import GroupedModelMultipleChoiceField


class CombinatorForm(forms.Form):

    drugs = GroupedModelMultipleChoiceField(
        queryset=Drug.objects,
        choices_groupby='category'
    )
