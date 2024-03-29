from operator import attrgetter

from django.contrib.auth import get_user_model
from django.db.models import (
    CASCADE,
    SET_NULL,
    BooleanField,
    CharField,
    CheckConstraint,
    DateTimeField,
    F,
    ForeignKey,
    IntegerChoices,
    IntegerField,
    JSONField,
    ManyToManyField,
    Model,
    Q,
    SlugField,
    TextField,
    UniqueConstraint,
)
from django.db.models.fields import URLField
from django.db.models.fields.related import OneToOneField
from django.urls import reverse
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from mdanchors import AnchorConverter

from drugcombinator.managers import DrugManager, InteractionManager
from drugcombinator.modelfields import ListField
from drugcombinator.tasks import ping_webarchive
from drugcombinator.utils import get_libravatar_url, markdown_allowed


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
        default='',
        blank=True,
        verbose_name=_("description"),
        help_text=markdown_allowed()
    )
    risks = TextField(
        default='',
        blank=True,
        verbose_name=_("general risks"),
        help_text=format_lazy(
            '{text}<br/>{notice}',
            text=_(
                "Risks specific to combinations involving this substance "
                "that do not depend on a specific interaction."),
            notice=markdown_allowed()
        )
    )
    effects = TextField(
        default='',
        blank=True,
        verbose_name=_("general effects"),
        help_text=format_lazy(
            '{text}<br/>{notice}',
            text=_(
                "Effects specific to combinations involving this "
                "substance that do not depend on a specific "
                "interaction."),
            notice=markdown_allowed()
        )
    )
    aliases = ListField(
        verbose_name=_("aliases"),
        help_text=_("One alias per line. No need to duplicate case.")
    )
    interactants = ManyToManyField(
        'self',
        symmetrical=True,
        through='Interaction',
        verbose_name=_("interactants")
    )
    category = ForeignKey(
        'Category',
        SET_NULL,
        null=True,
        blank=True,
        related_name='drugs',
        verbose_name=_("category")
    )
    common = BooleanField(
        default=True,
        verbose_name=_("common"),
        help_text=_(
            "Common substances are displayed as buttons in the app.")
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

    def get_absolute_url(self, namespace=None):
        name = 'drug'
        if namespace:
            name = f"{namespace}:{name}"

        return reverse(name, kwargs={'slug': self.slug})

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
        'Drug',
        CASCADE,
        related_name='interactions_from',
        verbose_name=_("first interactant")
    )
    to_drug = ForeignKey(
        'Drug',
        CASCADE,
        related_name='interactions_to',
        verbose_name=_("second interactant")
    )
    names = ListField(
        verbose_name=_("slang names"),
        help_text=_(
            "One name per line. The first one can be emphasized in the "
            "app.")
    )
    risk = IntegerField(
        choices=Risk.choices,
        default=Risk.UNKNOWN,
        verbose_name=_("risks")
    )
    synergy = IntegerField(
        choices=Synergy.choices,
        default=Synergy.UNKNOWN,
        verbose_name=_("synergy")
    )
    risk_reliability = IntegerField(
        choices=Reliability.choices,
        default=Reliability.UNKNOWN,
        verbose_name=_("risks reliability")
    )
    effects_reliability = IntegerField(
        choices=Reliability.choices,
        default=Reliability.UNKNOWN,
        verbose_name=_("synergy and effects reliability")
    )
    risk_description = TextField(
        default='',
        blank=True,
        verbose_name=_("risks description"),
        help_text=markdown_allowed()
    )
    effect_description = TextField(
        default='',
        blank=True,
        verbose_name=_("effects description"),
        help_text=markdown_allowed()
    )
    notes = TextField(
        default='',
        blank=True,
        verbose_name=_("notes"),
        help_text=_(
            "This field is only displayed on this admin site and is "
            "shared between all users and languages.")
    )
    is_draft = BooleanField(
        default=True,
        verbose_name=_("draft"),
        help_text=_(
            "In case of work-in-progress, uncertain or incomplete "
            "data.")
    )
    uris = JSONField(
        default=dict,
        editable=False,
        verbose_name=_("URIs"),
        help_text=_(
            "URIs extracted from these interaction data texts, mapped "
            "to their last Wayback Machine snapshot date.")
    )

    # History manager will be added throug simple_history's register
    # function in translation.py, after the translated fields are
    # added by modeltranslation
    objects = InteractionManager()

    def __str__(self):
        return f"{self.from_drug.name} + {self.to_drug.name}"

    def get_absolute_url(self, namespace=None):
        name = 'combine'
        if namespace:
            name = f"{namespace}:{name}"

        return reverse(name, kwargs={
            'slugs': (self.from_drug.slug, self.to_drug.slug)
        })

    def other_interactant(self, drug):
        index = self.interactants.index(drug)
        return self.interactants[not index]

    @property
    def slug(self):
        return f"{self.from_drug.slug}_{self.to_drug.slug}"

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

    def extract_uris(self):
        """Extract URIs from this model `risk_description` and
        `effect_description` text fields."""

        return set().union(*(
            AnchorConverter(field).uris
            for field in (self.risk_description, self.effect_description)
        ))

    def update_uris(self):
        """Update stored URIs according to this model text fields.

        If a URI was already extracted, it will not be modified.
        Unused URIs will be removed.
        New URIs will be added with a `None` value.
        """
        self.uris = {
            uri: getattr(self.uris, uri, None)
            for uri in self.extract_uris()
        }

    def schedule_webarchive_ping(self):
        ping_webarchive(self.id, self.uris)()

    def save(self, process_uris=True, *args, **kwargs):
        self.sort_interactants()

        if process_uris:
            self.update_uris()

        super().save(*args, **kwargs)

        if process_uris:
            self.schedule_webarchive_ping()

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
        default='',
        blank=True,
        verbose_name=_("description")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")


class Note(LastModifiedModel):
    title = CharField(
        max_length=128,
        default=_("Untitled note"),
        verbose_name=_("title")
    )
    content = TextField(
        default='',
        blank=True,
        verbose_name=_("content"),
        help_text=_(
            "Notes are only displayed on this admin site and are shared "
            "between all users and languages.")
    )
    related_drugs = ManyToManyField(
        'Drug',
        related_name='notes',
        blank=True,
        verbose_name=_("involved substances"),
        help_text=_(
            "If this note involves specific substances, you can "
            "optionally set them here.")
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("note")


class Contributor(Model):
    user = OneToOneField(
        get_user_model(),
        CASCADE,
        related_name='profile',
        verbose_name=_("user")
    )
    page = URLField(
        default='',
        blank=True,
        max_length=128,
        verbose_name=_("personal page"),
        help_text=_(
            "This link may be used in public contributors lists.")
    )
    display = BooleanField(
        default=False,
        verbose_name=_("show publicly"),
        help_text=_("Show this profile in public contributors lists.")
    )

    @property
    def avatar_url(self):
        return get_libravatar_url(
            email=self.user.email,
            https=True,
            size=150,
            default='identicon'
        )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("contributor profile")
        verbose_name_plural = _("contributor profiles")
