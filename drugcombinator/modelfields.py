from django.db.models import TextField
from django.forms import ValidationError
from django.utils.translation import gettext as _


class ListField(TextField):

    DEFAULT_SEP = '\n'

    description = _("A list of values separated by %(sep)s.")


    def __init__(self, sep=DEFAULT_SEP, default=[], *args, **kwargs):

        self.sep = sep
        kwargs['blank'] = True
        kwargs['default'] = default

        super().__init__(*args, **kwargs)


    def deconstruct(self):

        name, path, args, kwargs = super().deconstruct()      

        if self.sep != self.DEFAULT_SEP:
            kwargs['sep'] = self.sep
        del kwargs['blank']

        return name, path, args, kwargs


    @property
    def non_db_attrs(self):

        return super().non_db_attrs + ('sep',)


    def from_db_value(self, value, expression, connection):

        return self.to_python(value)


    def to_python(self, value):
        if isinstance(value, list):
            return value

        if isinstance(value, str):
            if not value:
                return []
            return value.split(self.sep)

        raise ValidationError(f"Invalid value {value}")


    def get_prep_value(self, value):

        if not value:
            value = []
        return self.sep.join(map(str, value))
