from django.db.models import (Model, CASCADE, CharField, DateTimeField,
    OneToOneField)
from django.urls import reverse


class Portal(Model):

    name = CharField(
        max_length = 128,
        verbose_name = "nom"
    )
    drug = OneToOneField(
        'drugcombinator.Drug', CASCADE,
        related_name = 'portal',
        verbose_name = "substance"
    )
    last_modified = DateTimeField(
        auto_now = True,
        verbose_name = "dernière modification"
    )


    def __str__(self):
        return self.name


    def get_absolute_url(self):
        return reverse('portal', kwargs={'drug': self.drug.slug})
    

    class Meta:
        verbose_name = "portail"
