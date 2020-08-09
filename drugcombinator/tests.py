from django.test import TestCase
from django.db.utils import IntegrityError
from drugcombinator.utils import normalize
from drugcombinator.models import Drug, Interaction


class UtilsTestCase(TestCase):

    def test_normalize(self):

        self.assertEqual(
            normalize("Je bois du café. Ça vous va ?"),
            "je bois du cafe. ca vous va ?"
        )


    def test_normalize_noop(self):

        data = "c'est vraiment pas de bol !"
        self.assertEqual(normalize(data), data)


class InteractionModelTestCase(TestCase):

    drug_a = Drug(name="DrugA", slug='drug-a')
    drug_b = Drug(name="DrugB", slug='drug-b')
    drug_c = Drug(name="DrugC", slug='drug-c')
    inter_a_b = Interaction(
        from_drug=drug_a,
        to_drug=drug_b
    )
    inter_b_c = Interaction(
        from_drug=drug_b,
        to_drug=drug_c
    )


    def setUp(self):

        self.drug_a.save()
        self.drug_b.save()
        self.drug_c.save()
        self.inter_a_b.save()
        self.inter_b_c.save()

        

    def test_interactants_inequals(self):

        with self.assertRaises(IntegrityError):
            Interaction(
                from_drug=self.drug_a,
                to_drug=self.drug_a
            ).save()
        

    def test_interactants_unique_together(self):

        with self.assertRaises(IntegrityError):
            Interaction(
                from_drug=self.drug_b,
                to_drug=self.drug_a
            ).save()
        

    def test_interactants_ordering(self):

        inter = Interaction(
            from_drug=self.drug_c,
            to_drug=self.drug_a
        )
        inter.save()
        self.assertSequenceEqual(
            inter.interactants,
            sorted(inter.interactants, key=lambda d: d.name)
        )
        

    def test_interactants_fetching(self):

        self.assertEqual(
            self.drug_b.all_interactants.count(),
            self.drug_b.interactions.count(),
        )
        

    def test_interactants_fetching_django_not_fixed(self):

        self.assertNotEqual(
            self.drug_b.all_interactants.count(),
            self.drug_b.interactants.count(),
            "The Django framework now seems to support recursive M2M " \
            "fields better. The Drug.all_interactants tweak is maybe " \
            "not needed anymore."
        )
