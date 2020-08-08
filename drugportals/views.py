from django.shortcuts import render
from django.http import Http404
from drugportals.models import Portal


def portal(request, drug):

    try:
        portal = Portal.objects.get(drug__slug=drug)
    except Portal.DoesNotExist:
        raise Http404("Ce portail n'existe pas.")
    
    return render(request, 'drugportals/portals.html', locals())
