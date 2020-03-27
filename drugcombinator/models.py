from django.db.models import (Model, DateTimeField, CharField,
        ForeignKey, CASCADE, SET_NULL, SlugField, TextField, 
        ManyToManyField, IntegerField, PositiveIntegerField, Max)
from django.db import OperationalError
from django.urls import reverse


class Drug(Model):

    added = DateTimeField(auto_now_add=True, verbose_name="ajouté")
    name = CharField(max_length=128, verbose_name="nom")
    slug = SlugField(unique=True, verbose_name="identifiant")
    description = TextField(default='', blank=True, verbose_name="description")
    _aliases = TextField(default='', blank=True, verbose_name="dénominations", help_text="Un alias par ligne. Insensible à la casse.")
    interactants = ManyToManyField('self', symmetrical=False, through='Interaction', verbose_name="interactants")
    category = ForeignKey('Category', SET_NULL, null=True, blank=True, related_name='substances', verbose_name="catégorie")


    def __str__(self):
        return self.name
    

    @property
    def aliases(self):
        return self._aliases.split('\n')
    aliases.fget.short_description = "Dénominations"
    
    @aliases.setter
    def set_aliases(self, value):
        if isinstance(value, str):
            self._aliases = value
        else:
            self._aliases = '\n'.join(value)


    def get_absolute_url(self):
        return reverse('substance', kwargs={'slug': self.slug})


    class Meta:
        verbose_name = "substance"


PHARMACOLOGY_UNKNOWN = 0
PHARMACOLOGY_NEUTRAL = 1
PHARMACOLOGY_DECREASE = 2
PHARMACOLOGY_INCREASE = 3
PHARMACOLOGY_MIXED = 4
PHARMACOLOGY = (
    (PHARMACOLOGY_UNKNOWN, 'Inconnue'),
    (PHARMACOLOGY_NEUTRAL, 'Neutre'),
    (PHARMACOLOGY_DECREASE, 'Atténuation'),
    (PHARMACOLOGY_INCREASE, 'Potentialisation'),
    (PHARMACOLOGY_MIXED, 'Mixte'),
)

RISK_UNKNOWN = 0
RISK_NEUTRAL = 1
RISK_CAUTION = 2
RISK_UNSAFE = 3
RISK_DANGEROUS = 4
RISK = (
    (RISK_UNKNOWN, 'Inconnu'),
    (RISK_NEUTRAL, 'Neutre'),
    (RISK_CAUTION, 'Vigilance'),
    (RISK_UNSAFE, 'Risqué'),
    (RISK_DANGEROUS, 'Dangereux'),
)


class SymetricalRelationModel(Model):
    """
        This ABC is intended to automatically create, update and delete a copy of
        each instance with swapped ForeignKeys, describing a reciprocal relation
        between other objects.
        Inherited classes need to set a tuple named symetrical_fields containing
        two of their model fields name, such as:
        symetrical_fields = ('from_object', 'to_object')
    """

    sym_id = PositiveIntegerField(default=0, editable=False)
    symetrical_fields = ()


    def save(self, *args, **kwargs):

        if not self.sym_id: # Not saved to the database yet
            max_id = type(self).get_max_sym_id()
            self.sym_id = max_id + 1
        
        super(SymetricalRelationModel, self).save(*args, **kwargs)

        sym = self
        existing_syms = self.get_existing_syms()

        if not existing_syms:
            sym.pk = None
        elif len(existing_syms) == 1:
            sym.pk = existing_syms[0].pk
        else:
            raise OperationalError(f"Object has more than one symetrical ({len(existing_syms)} found)")

        fields_names = sym.symetrical_fields
        assert len(fields_names) == 2
        fields = [getattr(self, name) for name in fields_names]
        setattr(self, fields_names[0], fields[1])
        setattr(self, fields_names[1], fields[0])

        super(SymetricalRelationModel, sym).save(*args, **kwargs)
    

    def delete(self, *args, **kwargs):

        for sym in self.get_existing_syms():
            super(SymetricalRelationModel, sym).delete(*args, **kwargs)
        
        super(SymetricalRelationModel, self).delete(*args, **kwargs)


    def get_existing_syms(self):
        return type(self).objects.filter(sym_id=self.sym_id).exclude(pk=self.pk)


    @classmethod
    def get_max_sym_id(cls):
        return cls.objects.all().aggregate(largest=Max('sym_id'))['largest'] or 0


    class Meta:
        abstract = True
        ordering = ('sym_id',)


class Interaction(SymetricalRelationModel):

    added = DateTimeField(auto_now_add=True, verbose_name="ajouté")
    from_substance = ForeignKey('Drug', CASCADE, related_name='from_interaction+', verbose_name="première substance")
    to_substance = ForeignKey('Drug', CASCADE, related_name='to_interaction+', verbose_name="seconde substance")
    risk = IntegerField(choices=RISK, default=RISK_UNKNOWN, verbose_name="risques")
    pharmaco = IntegerField(choices=PHARMACOLOGY, default=PHARMACOLOGY_UNKNOWN, verbose_name="pharmacologie")
    risk_description = TextField(default='', blank=True, verbose_name="description des risques")
    effect_description = TextField(default='', blank=True, verbose_name="description des effets")

    symetrical_fields = ('from_substance', 'to_substance')


    def __str__(self):
        return f"{self.from_substance.name} + {self.to_substance.name}"


    class Meta:
        unique_together = ('from_substance', 'to_substance')
        verbose_name = "interaction"


class Category(Model):

    added = DateTimeField(auto_now_add=True, verbose_name="ajouté")
    name = CharField(max_length=128, verbose_name="nom")
    slug = SlugField(unique=True, verbose_name="identifiant")
    description = TextField(default='', blank=True, verbose_name="description")


    def __str__(self):
        return self.name


    class Meta:
        verbose_name = "catégorie"
