from django.db.models import (Model, DateTimeField, CharField, ForeignKey,
    CASCADE, SET_NULL, SlugField, TextField, ManyToManyField, IntegerField,
    PositiveIntegerField, BooleanField, Max, CheckConstraint, F, Q,
    UniqueConstraint, IntegerChoices)
from django.db import OperationalError
from django.urls import reverse
from django.template.loader import render_to_string
from simple_history.models import HistoricalRecords
from operator import attrgetter
from drugcombinator.managers import DrugManager, InteractionManager
from drugcombinator.utils import markdown_allowed


class LastModifiedModel(Model):

    last_modified = DateTimeField(
        auto_now=True,
        verbose_name="dernière modification"
    )

    class Meta:
        abstract = True


class Drug(LastModifiedModel):
    
    name = CharField(
        max_length=128,
        verbose_name="nom"
    )
    slug = SlugField(
        unique=True,
        verbose_name="identifiant"
    )
    description = TextField(
        default='', blank=True,
        verbose_name="description",
        help_text=markdown_allowed()
    )
    risks = TextField(
        default='', blank=True,
        verbose_name="risques généraux",
        help_text="Risques spécifiques à la combinaison de cette " \
            "substance qui ne dépendent pas d'une interaction " \
            "particulière.<br/>"
            + markdown_allowed()
    )
    effects = TextField(
        default='', blank=True,
        verbose_name="effets généraux",
        help_text="Effets spécifiques à la combinaison de cette " \
            "substance qui ne dépendent pas d'une interaction " \
            "particulière.<br/>"
            + markdown_allowed()
    )
    _aliases = TextField(
        default='', blank=True,
        verbose_name="dénominations",
        help_text="Un alias par ligne. Insensible à la casse."
    )
    interactants = ManyToManyField(
        'self',
        symmetrical=True, through='Interaction',
        verbose_name="interactants"
    )
    category = ForeignKey(
        'Category', SET_NULL,
        null=True, blank=True, related_name='drugs',
        verbose_name="catégorie"
    )
    common = BooleanField(
        default=True,
        verbose_name="commune",
        help_text="Les substances communes sont affichées sous forme " \
            "de boutons dans l'app."
    )

    history = HistoricalRecords()
    objects = DrugManager()


    def __str__(self):
        return self.name
    

    @property
    def interactions(self):
        return self.interactions_from.all() | self.interactions_to.all()
    

    @property
    def aliases(self):
        als = self._aliases.split('\n')
        return [al.strip() for al in als if al]
    aliases.fget.short_description = "Dénominations"
    
    @aliases.setter
    def set_aliases(self, value):
        if isinstance(value, str):
            self._aliases = value.strip()
        else:
            self._aliases = '\n'.join([v.strip() for v in value])


    def get_absolute_url(self):
        return reverse('drug', kwargs={'name': self.slug})


    class Meta:
        verbose_name = "substance"
        ordering = ('name',)


class Interaction(LastModifiedModel):

    class Synergy(IntegerChoices):

        UNKNOWN = (0, "Inconnue")
        NEUTRAL = (1, "Neutre")
        ADDITIVE = (5, "Addition")
        DECREASE = (2, "Atténuation")
        INCREASE = (3, "Potentialisation")
        MIXED = (4, "Mixte")


    class Risk(IntegerChoices):

        UNKNOWN = (0, "Inconnu")
        NEUTRAL = (1, "Neutre")
        CAUTION = (2, "Vigilance")
        UNSAFE = (3, "Risqué")
        DANGEROUS = (4, "Dangereux")


    class Reliability(IntegerChoices):

        UNKNOWN = (0, "Non évaluée")
        HYPOTHETICAL = (1, "Théorique")
        INFERRED = (2, "Supposée")
        PROVEN = (3, "Avérée")


    from_drug = ForeignKey(
        'Drug', CASCADE,
        related_name='interactions_from',
        verbose_name="première substance"
    )
    to_drug = ForeignKey(
        'Drug', CASCADE,
        related_name='interactions_to',
        verbose_name="seconde substance"
    )
    risk = IntegerField(
        choices=Risk.choices, default=Risk.UNKNOWN,
        verbose_name="risques"
    )
    synergy = IntegerField(
        choices=Synergy.choices, default=Synergy.UNKNOWN,
        verbose_name="synergie"
    )
    risk_reliability = IntegerField(
        choices=Reliability.choices, default=Reliability.UNKNOWN,
        verbose_name="fiabilité des risques"
    )
    effects_reliability = IntegerField(
        choices=Reliability.choices, default=Reliability.UNKNOWN,
        verbose_name="fiabilité de la synergie et des effets"
    )
    risk_description = TextField(
        default='', blank=True,
        verbose_name="description des risques",
        help_text=markdown_allowed()
    )
    effect_description = TextField(
        default='', blank=True,
        verbose_name="description des effets",
        help_text=markdown_allowed()
    )
    notes = TextField(
        default='', blank=True,
        verbose_name="notes",
        help_text="Ce champ n'est visible que sur ce site " \
            "d'administration et est partagé entre tous les " \
            "utilisateurs."
    )
    is_draft = BooleanField(
        default=True,
        verbose_name="brouillon",
        help_text="En cas de travail en cours, de données incertaines" \
            " ou incomplètes."
    )

    history = HistoricalRecords()
    objects = InteractionManager()


    def __str__(self):
        return f"{self.from_drug.name} + {self.to_drug.name}"
    

    def get_absolute_url(self):
        return reverse('combine', kwargs={
            'slugs': (self.from_drug.slug, self.to_drug.slug)
        })
    

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
        interactants = sorted(interactants, key=attrgetter('name'))
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
        verbose_name = "interaction"


class Category(LastModifiedModel):

    name = CharField(
        max_length=128,
        verbose_name="nom"
    )
    slug = SlugField(
        unique=True,
        verbose_name="identifiant"
    )
    description = TextField(
        default='', blank=True,
        verbose_name="description"
    )


    def __str__(self):
        return self.name


    class Meta:
        verbose_name = "catégorie"


class Note(LastModifiedModel):

    title = CharField(
        max_length=128, default="Note sans titre",
        verbose_name="titre"
    )
    content = TextField(
        default='', blank=True,
        verbose_name="contenu",
        help_text="Les notes ne sont visibles que sur ce site " \
            "d'administration et sont partagées entre tous les " \
            "utilisateurs."
    )
    related_drugs = ManyToManyField(
        'Drug',
        related_name='notes', blank=True,
        verbose_name="substances concernées",
        help_text="Si cette note concerne des substances " \
            "particulières, vous pouvez optionellement les spécifier " \
            "ici."
    )


    def __str__(self):
        return self.title


    class Meta:
        verbose_name = "note"
