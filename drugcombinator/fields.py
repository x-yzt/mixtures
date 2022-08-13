from operator import attrgetter
from functools import partial
from itertools import groupby

from django.forms.fields import CharField
from django.forms.models import (ModelChoiceIterator,
    ModelMultipleChoiceField)


class GroupedModelChoiceIterator(ModelChoiceIterator):

    def __init__(self, field, groupby):

        self.groupby = groupby
        super().__init__(field)

    def __iter__(self):

        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        
        queryset = self.queryset

        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        
        for group, objs in groupby(queryset, self.groupby):
            yield (group, [self.choice(obj) for obj in objs])


class GroupedModelMultipleChoiceField(ModelMultipleChoiceField):

    def __init__(self, *args, choices_groupby, **kwargs):

        if isinstance(choices_groupby, str):
            choices_groupby = attrgetter(choices_groupby)
        
        elif not callable(choices_groupby):
            raise TypeError(
                "choices_groupby must be a str or a callable accepting " \
                "a single argument"
            )
        
        self.iterator = partial(
            GroupedModelChoiceIterator,
            groupby=choices_groupby
        )
        super().__init__(*args, **kwargs)


class ListField(CharField):
    
    def __init__(self, sep, *args, **kwargs):
    
        self.sep = sep
        super().__init__(*args, **kwargs)
    

    def prepare_value(self, value):
    
        return self.sep.join(value)


    def to_python(self, value):

        if not value:
            return []
        return [
            item.strip() for item in value.split(self.sep)
            if item.strip()
        ]
