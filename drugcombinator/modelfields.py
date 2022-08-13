from django.db.models import TextField
from django.utils.translation import gettext as _


class ListField(TextField):

    DEFAULT_SEP = '\n'

    description = _("A list of values separated by %(sep)s.")


    def __init__(self, sep=DEFAULT_SEP, default=[], *args, **kwargs):

        self.sep = sep
        kwargs['blank'] = True

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
        
        return value.split(self.sep)


    def to_python(self, value):
        
        if isinstance(value, str):
            return value.split(self.sep)
        return value


    def get_prep_value(self, value):

        if value is None:
            value = []
        return self.sep.join(value)
