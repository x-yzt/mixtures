from collections.abc import Iterable

from django.db.models import QuerySet, Model


class URIDictSerializer:
    def serialize(self, obj, attrs):
        return {
            attr: self._transform(getattr(obj, attr))
            for attr in attrs
        }
        
    def _transform(self, value):        
        if isinstance(value, QuerySet):
            return [self._transform(o) for o in value]
        
        if isinstance(value, Model):
            try:
                return value.get_absolute_url()
            except AttributeError:
                return str(value)
            
        return value


class StructureDictSerializer:
    def serialize(self, obj, structure, select_related={}):
        data = {}

        for key, struct in structure.items():
            if struct is None:
                data[key] = self._transform(getattr(obj, key))
            
            elif isinstance(struct, (dict, tuple)):
                relations = select_related.get(key, ())
                queryset = getattr(obj, key).select_related(*relations)

                if isinstance(struct, dict):
                    data[key] = [
                        self.serialize(o, struct)
                        for o in queryset
                    ]
                
                else:
                    assert len(struct) == 2
                    okey, ostruct = struct
                    data[key] = {
                        self._transform(getattr(o, okey)):
                        self.serialize(o, ostruct)
                        for o in queryset
                    }
                    
            else:
                raise ValueError(
                    "Substructure must be `None`, `dict` or 2-`tuple`, "
                    f"not `{type(struct)}`"
                )
        
        return data
    
    def _transform(self, value):
        if isinstance(value, Model):
            return str(value)
        
        if isinstance(value, Iterable) and not isinstance(value, str):
            return tuple(self._transform(v) for v in value)
        
        return value
