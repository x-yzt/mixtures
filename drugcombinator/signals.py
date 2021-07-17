from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from drugcombinator.models import Contributor


@receiver(post_save, sender=get_user_model())
def create_contributor_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        profile = Contributor(user=instance)
        profile.save()
