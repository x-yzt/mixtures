from django.db.models import Manager
from drugcombinator.utils import normalize
from django.http import Http404


class DrugManager(Manager):

    def get_from_name(self, name):
        """
            Return a drug based on its name.
            Search criterias priorities:
                - equal to slug (case insensitive, accentuation insensitive)
                - equal to name (case insentitive)
                - included in aliases (case insentitive)
            Throw DoesNotExist if no drug is found.
        """

        try:
            return self.get(slug=normalize(name))
        except self.model.DoesNotExist:
            pass

        try:
            return self.filter(name__iexact=name)[0]    
        except IndexError:
            pass

        reg = rf'(^|\r|\n){name}(\r|\n|$)'
        try:
            return self.filter(_aliases__iregex=reg)[0]
        except IndexError:
            raise self.model.DoesNotExist
    

    def get_from_name_or_404(self, name):
        """
            Similar to get_from_name but raises Http404 if no drug is found.
        """

        try:
            return self.get_from_name(name)
        except self.model.DoesNotExist:
            raise Http404(f"Unable to find drug {name}.")
