"""As the `drugportals` app is designed to work with subdomains, this
must be used as a root URLconf and is not designed to be included in
other URLconfs.
"""

from django.conf.urls.i18n import i18n_patterns
from django.urls import path

from drugportals import views


urlpatterns = i18n_patterns(
    path('', views.portal, name='portal'),
)
