from collections.abc import Callable, Iterable

from django.db.models import Model, QuerySet


class URIDictSerializer:
    def __init__(self, attrs):
        """Simple serializer that serializes objects by accessing a
        specified tuple of attributes.

        Fields describing a relationship will be replaced by URIs
        pointing to the object they relate.
        """
        self.attrs = attrs

    def serialize(self, obj):
        return {
            attr: self._transform(getattr(obj, attr))
            for attr in self.attrs
        }

    def serialize_many(self, objs):
        return tuple(self.serialize(obj) for obj in objs)

    def _transform(self, value):
        if isinstance(value, QuerySet):
            return self.serialize_many(value)

        if isinstance(value, Model):
            try:
                return value.get_absolute_url()
            except AttributeError:
                return str(value)

        return value


class StructureSerializer:
    def __init__(self, structure, select_related=None):
        """Simple serializer that serializes objects according to a
        specified structure.

        This allows specifying a nested hierarchy of models by
        traversing relationships.

        The `structure` must be a tuple that contains either:
            - Strings matching object fields or attributes;
            - Callables taking a model instance in parameter and
            returning a `('key', value)` tuple where:
                - `'key'` is an identifier that will be used as key in
                the serialized output;
                - `value` will be used as value. It will be
                postprocessed by the serializer as regular fields do;
            - 2-tuples `('field', 'related_field')` where:
                - `'field'` is a field of the model that will result in
                a `QuerySet` of related objects when accessed;
                - `'related_field'` is a field of the related model.
                The value of this field will be used to represent the
                related objects;
            - 3-tuples `('field', 'related_field', substructure)` where:
                - 'related_field' is a field as described above, that
                will ve used as a key to identify related objects. If it
                is `None`, objects will not have keys.
                - `substructure` is a structure recursively matching
                this description, specifying the structure to use to
                serialize the related objects.

        The `select_related` parameter is an optionnal dict
        `{'field': related_fields}` where:
            - `'field'` is a field of the model that defines a
            relationship;
            - `related_field` is a tuple containing field of the related
            model to prefetch. This is used to reduce database queries
            count.
        """
        self.structure = structure
        self.select_related = select_related or {}

    def serialize(self, obj, structure=None):
        """Serializes an object.

        The `structure` parameter will override the serializer structure
        if specified.
        """
        structure = structure or self.structure
        assert isinstance(structure, tuple)

        data = {}

        for item in structure:
            assert isinstance(item, str | tuple | Callable)

            if isinstance(item, tuple):
                assert 2 <= len(item) <= 3
                field, key, substructure, *_ = [*item, None]

                queryset = getattr(obj, field)

                # This allows duck typing for model attributes returning
                # iterables instead of true QuerySets
                if hasattr(queryset, 'select_related'):
                    relations = self.select_related.get(item, ())
                    queryset.select_related(*relations)

                if substructure is None:
                    assert key is not None
                    data[field] = self.serialize_single_key(queryset, key)

                else:
                    data[field] = (
                        self.serialize_many(queryset, key, substructure)
                    )

            elif callable(item):
                key, val = item(obj)
                data[key] = self._transform(val)

            else:
                data[item] = self._transform(getattr(obj, item))

        return data

    def serialize_many(self, objs, key=None, structure=None):
        """Serializes a collection of objects or a `QuerySet`.

        If `key` is specified, it will return a `dict` which keys will
        be populated by lookups on that field. Otherwise, returns a bare
        `tuple`.
        """
        structure = structure or self.structure

        if not key:
            return tuple(self.serialize(obj, structure) for obj in objs)

        return {
            self._transform(getattr(obj, key)):
            self.serialize(obj, structure)
            for obj in objs
        }

    def serialize_single_key(self, objs, key):
        """Serializes a collection of objects or a `QuerySet`.

        Output is a tuple where each object is represented by a lookup
        on a single `key`.
        """
        return tuple(self._transform(getattr(obj, key)) for obj in objs)

    def _transform(self, value):
        if isinstance(value, Model):
            return str(value)

        if isinstance(value, Iterable) and not isinstance(value, str):
            return tuple(self._transform(v) for v in value)

        return value
