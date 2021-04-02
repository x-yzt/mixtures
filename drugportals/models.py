from django.db.models import (Model, CASCADE, CharField, DateTimeField,
    OneToOneField)
from django.utils.translation import gettext_lazy as _
from django_hosts.resolvers import reverse


class Portal(Model):

    name = CharField(
        max_length = 128,
        verbose_name = _("name")
    )
    drug = OneToOneField(
        'drugcombinator.Drug', CASCADE,
        related_name = 'portal',
        verbose_name = _("substance")
    )
    last_modified = DateTimeField(
        auto_now = True,
        verbose_name = _("last modification")
    )


    def __str__(self):
        return self.name


    def get_absolute_url(self):
        return reverse('portal',
            host='portals', host_kwargs={'drug': self.drug.slug},
        )
    

    class Meta:
        verbose_name = _("portal")
