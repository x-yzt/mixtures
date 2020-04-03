from django import forms
from drugcombinator.models import Drug
from drugcombinator.fields import GroupedModelMultipleChoiceField


class CombinatorForm(forms.Form):

    drugs_field = GroupedModelMultipleChoiceField(
        queryset=Drug.objects,
        choices_groupby='category',
        label="Drogues à combiner"
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['drugs_field'].empty_label = "Sélectionnez des substances"
