from operator import attrgetter
from django.db.models import (Model, DateTimeField, CharField, ForeignKey,
    CASCADE, SET_NULL, SlugField, TextField, ManyToManyField, IntegerField,
    BooleanField, CheckConstraint, F, Q, UniqueConstraint, IntegerChoices)
from django.urls import reverse
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.template.loader import render_to_string

from drugcombinator.managers import DrugManager, InteractionManager
from drugcombinator.utils import markdown_allowed



class LastModifiedModel(Model):

    last_modified = DateTimeField(
        auto_now=True,
        verbose_name=_("last modification")
    )

    class Meta:
        abstract = True


class Drug(LastModifiedModel):
    
    name = CharField(
        max_length=128,
        verbose_name=_("name")
    )
    slug = SlugField(
        unique=True,
        verbose_name=_("identifier")
    )
    description = TextField(
        default='', blank=True,
        verbose_name=_("description"),
        help_text=markdown_allowed()
    )
    risks = TextField(
        default='', blank=True,
        verbose_name=_("general risks"),
        help_text=format_lazy('{text}<br/>{notice}',
            text=_("Risks specific to combinations involving this "
                "substance that do not depend on a specific "
                "interaction."),
            notice=markdown_allowed()
        )
    )
    effects = TextField(
        default='', blank=True,
        verbose_name=_("general effects"),
        help_text=format_lazy('{text}<br/>{notice}',
            text=_("Effects specific to combinations involving this "
                "substance that do not depend on a specific "
                "interaction."),
            notice=markdown_allowed()
        )
    )
    _aliases = TextField(
        default='', blank=True,
        verbose_name=_("aliases"),
        help_text=_("One alias per line. No need to duplicate case.")
    )
    interactants = ManyToManyField(
        'self',
        symmetrical=True, through='Interaction',
        verbose_name=_("interactants")
    )
    category = ForeignKey(
        'Category', SET_NULL,
        null=True, blank=True, related_name='drugs',
        verbose_name=_("category")
    )
    common = BooleanField(
        default=True,
        verbose_name=_("common"),
        help_text=_("Common substances are displayed as buttons in the "
            "app.")
    )

    # History manager will be added through simple_history's register
    # function in translation.py, after the translated fields are
    # added by modeltranslation
    objects = DrugManager()


    def __str__(self):
        return self.name
    

    @property
    def interactions(self):
        return Interaction.objects.filter(
            Q(from_drug=self) | Q(to_drug=self)
        )


    # In Django 3.1.0, the Drug.interactants field accessor only returns
    # Drug objects from the Interaction.to_drug field, but misses ones
    # from the Interaction.from_drug field. This property is a
    # workaround, as this limitation may be removed at framework level
    # one day.
    @property
    def all_interactants(self):
        return (
            self.interactants.all()
            | Drug.objects.filter(
                interactions_from__in=self.interactions_to.all()
            )
        )
    

    @property
    def aliases(self):
        als = self._aliases.split('\n')
        return [al.strip() for al in als if al]
    aliases.fget.short_description = _("Aliases")
    
    @aliases.setter
    def set_aliases(self, value):
        if isinstance(value, str):
            self._aliases = value.strip()
        else:
            self._aliases = '\n'.join([v.strip() for v in value])


    def get_absolute_url(self):
        return reverse('drug', kwargs={'name': self.slug})


    class Meta:
        verbose_name = _("substance")
        ordering = ('slug',)


class Interaction(LastModifiedModel):

    class Synergy(IntegerChoices):

        UNKNOWN = (0, pgettext_lazy("synergy", "Unknown"))
        NEUTRAL = (1, pgettext_lazy("synergy", "Neutral"))
        ADDITIVE = (5, _("Additive"))
        DECREASE = (2, _("Decrease"))
        INCREASE = (3, _("Increase"))
        MIXED = (4, _("Mixed"))


    class Risk(IntegerChoices):

        UNKNOWN = (0, pgettext_lazy("risk", "Unknown"))
        NEUTRAL = (1, pgettext_lazy("risk", "Neutral"))
        CAUTION = (2, _("Caution"))
        UNSAFE = (3, _("Unsafe"))
        DANGEROUS = (4, _("Dangerous"))


    class Reliability(IntegerChoices):

        UNKNOWN = (0, pgettext_lazy("reliability", "Unknown"))
        HYPOTHETICAL = (1, _("Hypothetical"))
        INFERRED = (2, _("Inferred"))
        PROVEN = (3, _("Proven"))


    from_drug = ForeignKey(
        'Drug', CASCADE,
        related_name='interactions_from',
        verbose_name=_("first interactant")
    )
    to_drug = ForeignKey(
        'Drug', CASCADE,
        related_name='interactions_to',
        verbose_name=_("second interactant")
    )
    risk = IntegerField(
        choices=Risk.choices, default=Risk.UNKNOWN,
        verbose_name=_("risks")
    )
    synergy = IntegerField(
        choices=Synergy.choices, default=Synergy.UNKNOWN,
        verbose_name=_("synergy")
    )
    risk_reliability = IntegerField(
        choices=Reliability.choices, default=Reliability.UNKNOWN,
        verbose_name=_("risks reliability")
    )
    effects_reliability = IntegerField(
        choices=Reliability.choices, default=Reliability.UNKNOWN,
        verbose_name=_("synergy and effects reliability")
    )
    risk_description = TextField(
        default='', blank=True,
        verbose_name=_("risks description"),
        help_text=markdown_allowed()
    )
    effect_description = TextField(
        default='', blank=True,
        verbose_name=_("effects description"),
        help_text=markdown_allowed()
    )
    notes = TextField(
        default='', blank=True,
        verbose_name=_("notes"),
        help_text=_("This field is only displayed on this admin site "
            "and is shared between all users and languages.")
    )
    is_draft = BooleanField(
        default=True,
        verbose_name=_("draft"),
        help_text=_("In case of work-in-progress, uncertain or "
            "incomplete data.")
    )

    # History manager will be added throug simple_history's register
    # function in translation.py, after the translated fields are
    # added by modeltranslation
    objects = InteractionManager()


    def __str__(self):
        return f"{self.from_drug.name} + {self.to_drug.name}"
    

    def get_absolute_url(self):
        return reverse('combine', kwargs={
            'slugs': (self.from_drug.slug, self.to_drug.slug)
        })
    

    def other_interactant(self, drug):
        index = self.interactants.index(drug)
        return self.interactants[not index]


    def get_contrib_email_body(self):
        return render_to_string(
            'drugcombinator/mail/contrib_body.txt',
            {'interaction': self}
        )
    

    @property
    def interactants(self):
        return (self.from_drug, self.to_drug)
    
    @interactants.setter
    def interactants(self, interactants):
        interactants = sorted(interactants, key=attrgetter('slug'))
        self.from_drug, self.to_drug = interactants


    def sort_interactants(self):
        # The interactants property setter will handle interactants
        # reordering
        self.interactants = self.interactants


    def save(self, *args, **kwargs):
        self.sort_interactants()        
        super().save(*args, **kwargs)

    
    @classmethod
    def get_dummy_risks(cls):
        return [cls(risk=risk) for risk in cls.Risk.values]

    @classmethod
    def get_dummy_synergies(cls):
        return [cls(synergy=synergy) for synergy in cls.Synergy.values]


    class Meta:
        constraints = (
            CheckConstraint(
                check=~Q(from_drug=F('to_drug')),
                name='interactants_inequals'
            ),
            UniqueConstraint(
                fields=('from_drug', 'to_drug'),
                name='interactants_unique_together'
            )
        )
        verbose_name = _("interaction")


class Category(LastModifiedModel):

    name = CharField(
        max_length=128,
        verbose_name=_("name")
    )
    slug = SlugField(
        unique=True,
        verbose_name=_("identifier")
    )
    description = TextField(
        default='', blank=True,
        verbose_name=_("description")
    )


    def __str__(self):
        return self.name


    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")


class Note(LastModifiedModel):

    title = CharField(
        max_length=128, default=_("Untitled note"),
        verbose_name=_("title")
    )
    content = TextField(
        default='', blank=True,
        verbose_name=_("content"),
        help_text=_("Notes are only displayed on this admin site and "
            "are shared between all users and languages.")
    )
    related_drugs = ManyToManyField(
        'Drug',
        related_name='notes', blank=True,
        verbose_name=_("involved substances"),
        help_text=_("If this note involves specific substances, you "
            "can optionally set them here.")
    )


    def __str__(self):
        return self.title


    class Meta:
        verbose_name = _("note")
